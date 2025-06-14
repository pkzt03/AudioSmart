from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename

import cv2
import numpy as np
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
from PIL import Image
import time
import subprocess
import uuid
from spleeter.separator import Separator
import platform
import urllib.request
import zipfile
import whisper

app = Flask(__name__)
CORS(app)  # 允许跨域

UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

IMAGE_UPLOAD_FOLDER = 'image_uploads'
IMAGE_RESULT_FOLDER = 'image_results'
os.makedirs(IMAGE_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(IMAGE_RESULT_FOLDER, exist_ok=True)

def ensure_ffmpeg():
    # 你的ffmpeg bin目录
    ffmpeg_bin = r'D:\AudioSmart\ffmpeg-7.1.1-essentials_build\bin'
    if not os.path.exists(os.path.join(ffmpeg_bin, 'ffmpeg.exe')):
        raise RuntimeError(f'ffmpeg.exe 未找到，请检查路径：{ffmpeg_bin}')
    # 添加到环境变量
    os.environ["PATH"] = ffmpeg_bin + os.pathsep + os.environ.get("PATH", "")

# 在 Flask 启动前调用
ensure_ffmpeg()

@app.route('/api/upload', methods=['POST'])
def upload_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)
    # 这里可以直接返回文件名，前端后续用于降噪请求
    return jsonify({'filename': filename})

@app.route('/api/denoise', methods=['POST'])
def denoise_audio():
    data = request.json
    filename = data.get('filename')
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_path = os.path.join(RESULT_FOLDER, f'denoised_{filename}')

    try:
        import librosa
        import soundfile as sf
        import noisereduce as nr
        import numpy as np

        # 读取音频
        y, sr = librosa.load(input_path, sr=None, mono=True)
        noise_sample = y[:int(sr * 0.5)] if len(y) > int(sr * 0.5) else y
        # 谱减法降噪
        y_denoised = nr.reduce_noise(y=y, sr=sr, y_noise=noise_sample, prop_decrease=1.0, stationary=False)
        y_denoised = np.clip(y_denoised, -1.0, 1.0)
        # 保存降噪后音频为WAV格式
        sf.write(output_path, y_denoised, sr)
        return jsonify({'result_filename': f'denoised_{filename}'})
    except Exception as e:
        return jsonify({'error': f'降噪失败: {str(e)}'}), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join(RESULT_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    return send_file(file_path, as_attachment=True)

@app.route('/api/image_upload', methods=['POST'])
def image_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    save_path = os.path.join(IMAGE_UPLOAD_FOLDER, filename)
    file.save(save_path)
    return jsonify({'filename': filename})

@app.route('/api/image_add_noise', methods=['POST'])
def image_add_noise():
    data = request.json
    filename = data.get('filename')
    noise_type = data.get('noise_type')
    input_path = os.path.join(IMAGE_UPLOAD_FOLDER, filename)
    img = cv2.imread(input_path)
    if img is None:
        return jsonify({'error': 'Image not found'}), 404
    if noise_type == 'salt':
        noisy = add_salt_noise(img, 10000)
        out_name = f'salt_{filename}'
    else:
        noisy = add_gaussian_noise(img, 0, 50)
        out_name = f'gauss_{filename}'
    out_path = os.path.join(IMAGE_RESULT_FOLDER, out_name)
    cv2.imwrite(out_path, noisy)
    return jsonify({'result_filename': out_name})

@app.route('/api/image_denoise', methods=['POST'])
def image_denoise():
    data = request.json
    filename = data.get('filename')
    noise_type = data.get('noise_type')
    input_path = os.path.join(IMAGE_UPLOAD_FOLDER, filename)
    img = cv2.imread(input_path)
    if img is None:
        return jsonify({'error': 'Image not found'}), 404

    if noise_type == 'salt':
        noisy = add_salt_noise(img, 10000)
    else:
        noisy = add_gaussian_noise(img, 0, 50)
    # 非局部均值去噪
    result = cv2.fastNlMeansDenoisingColored(noisy, None, 10, 10, 7, 21)
    out_name = f'nlm_{filename}'
    out_path = os.path.join(IMAGE_RESULT_FOLDER, out_name)
    cv2.imwrite(out_path, result)
    return jsonify({'result_filename': out_name})

@app.route('/api/image_download/<filename>', methods=['GET'])
def image_download(filename):
    file_path = os.path.join(IMAGE_RESULT_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    return send_file(file_path, as_attachment=True)

@app.route('/api/extract_audio', methods=['POST'])
def extract_audio():
    data = request.json
    filename = data.get('filename')
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_audio = os.path.join(RESULT_FOLDER, f'{os.path.splitext(filename)[0]}_audio.mp3')
    try:
        clip = VideoFileClip(input_path)
        clip.audio.write_audiofile(output_audio, codec='libmp3lame')
        return jsonify({'audio_filename': os.path.basename(output_audio)})
    except Exception as e:
        return jsonify({'error': f'音频提取失败: {str(e)}'}), 500

@app.route('/api/convert', methods=['POST'])
def convert_file():
    data = request.json
    filename = data.get('filename')
    target_format = data.get('target_format')
    filetype = data.get('filetype')  # 'audio', 'image', 'video'
    if not filename or not target_format or not filetype:
        return jsonify({'error': '参数不完整'}), 400

    if filetype == 'audio':
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        output_name = f"{os.path.splitext(filename)[0]}.{target_format}"
        output_path = os.path.join(RESULT_FOLDER, output_name)
        try:
            audio = AudioSegment.from_file(input_path)
            audio.export(output_path, format=target_format)
            return jsonify({'result_filename': output_name})
        except Exception as e:
            return jsonify({'error': f'音频转换失败: {str(e)}'}), 500

    elif filetype == 'image':
        input_path = os.path.join(IMAGE_UPLOAD_FOLDER, filename)
        output_name = f"{os.path.splitext(filename)[0]}.{target_format}"
        output_path = os.path.join(IMAGE_RESULT_FOLDER, output_name)
        try:
            img = Image.open(input_path)
            # Pillow格式映射
            format_map = {'jpg': 'JPEG', 'jpeg': 'JPEG', 'png': 'PNG', 'bmp': 'BMP'}
            save_format = format_map.get(target_format.lower(), target_format.upper())
            if save_format == 'JPEG':
                img = img.convert('RGB')
            img.save(output_path, format=save_format)
            return jsonify({'result_filename': output_name})
        except Exception as e:
            return jsonify({'error': f'图片转换失败: {str(e)}'}), 500

    elif filetype == 'video':
        # 这里只做音频提取为mp3的简单示例
        if target_format == 'mp3':
            input_path = os.path.join(UPLOAD_FOLDER, filename)
            output_name = f"{os.path.splitext(filename)[0]}_audio.mp3"
            output_path = os.path.join(RESULT_FOLDER, output_name)
            try:
                clip = VideoFileClip(input_path)
                clip.audio.write_audiofile(output_path, codec='libmp3lame')
                return jsonify({'result_filename': output_name})
            except Exception as e:
                return jsonify({'error': f'视频转音频失败: {str(e)}'}), 500
        else:
            return jsonify({'error': '暂不支持该视频格式转换'}), 400

    else:
        return jsonify({'error': '不支持的文件类型'}), 400

@app.route('/api/list_files', methods=['GET'])
def list_files():
    # folder参数: uploads, results, image_uploads, image_results
    folder = request.args.get('folder', 'uploads')
    if folder == 'uploads':
        path = UPLOAD_FOLDER
    elif folder == 'results':
        path = RESULT_FOLDER
    elif folder == 'image_uploads':
        path = IMAGE_UPLOAD_FOLDER
    elif folder == 'image_results':
        path = IMAGE_RESULT_FOLDER
    else:
        return jsonify({'error': '未知文件夹'}), 400

    files = []
    for fname in os.listdir(path):
        fpath = os.path.join(path, fname)
        if os.path.isfile(fpath):
            files.append({
                'filename': fname,
                'size': os.path.getsize(fpath),
                'mtime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(fpath)))
            })
    return jsonify({'files': files})

@app.route('/api/delete_file', methods=['POST'])
def delete_file():
    data = request.json
    folder = data.get('folder')
    filename = data.get('filename')
    if not folder or not filename:
        return jsonify({'error': '参数不完整'}), 400
    if folder == 'uploads':
        path = UPLOAD_FOLDER
    elif folder == 'results':
        path = RESULT_FOLDER
    elif folder == 'image_uploads':
        path = IMAGE_UPLOAD_FOLDER
    elif folder == 'image_results':
        path = IMAGE_RESULT_FOLDER
    else:
        return jsonify({'error': '未知文件夹'}), 400
    fpath = os.path.join(path, filename)
    if os.path.exists(fpath):
        os.remove(fpath)
        return jsonify({'success': True})
    else:
        return jsonify({'error': '文件不存在'}), 404

def add_salt_noise(img, num):
    out = img.copy()
    h, w = out.shape[:2]
    for i in range(num):
        x = np.random.randint(0, w)
        y = np.random.randint(0, h)
        out[y, x] = 255 if np.random.rand() > 0.5 else 0
    return out

def add_gaussian_noise(img, mean, sigma):
    gauss = np.random.normal(mean, sigma, img.shape).astype('uint8')
    noisy = cv2.add(img, gauss)
    return noisy

@app.route('/api/trim', methods=['POST'])
def trim_audio():
    data = request.json
    filename = data.get('filename')
    start = float(data.get('start', 0))
    end = float(data.get('end', 0))
    if not filename or end <= start:
        return jsonify({'error': '参数错误'}), 400
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_name = f"trim_{filename}"
    output_path = os.path.join(RESULT_FOLDER, output_name)
    try:
        audio = AudioSegment.from_file(input_path)
        trimmed = audio[start*1000:end*1000]
        trimmed.export(output_path, format=filename.split('.')[-1])
        return jsonify({'result_filename': output_name})
    except Exception as e:
        return jsonify({'error': f'裁剪失败: {str(e)}'}), 500

@app.route('/api/speed', methods=['POST'])
def speed_audio():
    data = request.json
    filename = data.get('filename')
    rate = float(data.get('rate', 1.0))
    if not filename or rate <= 0:
        return jsonify({'error': '参数错误'}), 400
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_name = f"speed_{filename}"
    output_path = os.path.join(RESULT_FOLDER, output_name)
    try:
        audio = AudioSegment.from_file(input_path)
        new_audio = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * rate)
        }).set_frame_rate(audio.frame_rate)
        new_audio.export(output_path, format=filename.split('.')[-1])
        return jsonify({'result_filename': output_name})
    except Exception as e:
        return jsonify({'error': f'变速失败: {str(e)}'}), 500

@app.route('/api/batch_denoise', methods=['POST'])
def batch_denoise():
    data = request.json
    filenames = data.get('filenames', [])
    results = []
    for filename in filenames:
        # 可直接调用已有 denoise_audio 逻辑
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        output_path = os.path.join(RESULT_FOLDER, f'denoised_{filename}')
        try:
            import librosa, soundfile as sf, noisereduce as nr, numpy as np
            y, sr = librosa.load(input_path, sr=None, mono=True)
            noise_sample = y[:int(sr * 0.5)] if len(y) > int(sr * 0.5) else y
            y_denoised = nr.reduce_noise(y=y, sr=sr, y_noise=noise_sample, prop_decrease=1.0, stationary=False)
            y_denoised = np.clip(y_denoised, -1.0, 1.0)
            sf.write(output_path, y_denoised, sr)
            results.append({'filename': filename, 'result': f'denoised_{filename}', 'success': True})
        except Exception as e:
            results.append({'filename': filename, 'error': str(e), 'success': False})
    return jsonify({'results': results})

@app.route('/api/image_crop', methods=['POST'])
def image_crop():
    data = request.json
    filename = data.get('filename')
    x = int(data.get('x', 0))
    y = int(data.get('y', 0))
    w = int(data.get('w', 0))
    h = int(data.get('h', 0))
    if not filename or w <= 0 or h <= 0:
        return jsonify({'error': '参数错误'}), 400
    input_path = os.path.join(IMAGE_UPLOAD_FOLDER, filename)
    output_name = f"crop_{filename}"
    output_path = os.path.join(IMAGE_RESULT_FOLDER, output_name)
    try:
        img = Image.open(input_path)
        cropped = img.crop((x, y, x + w, y + h))
        cropped.save(output_path)
        return jsonify({'result_filename': output_name})
    except Exception as e:
        return jsonify({'error': f'裁剪失败: {str(e)}'}), 500

@app.route('/api/video_clip', methods=['POST'])
def video_clip():
    """
    前端传入：
    {
        "filename": "xxx.mp4",
        "segments": [
            {"start": 3.5, "end": 10.2},
            {"start": 15.0, "end": 22.0}
        ]
    }
    返回 result_filename
    """
    data = request.json
    filename = data.get('filename')
    segments = data.get('segments', [])
    if not filename or not segments:
        return jsonify({'error': '参数不完整'}), 400

    input_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(input_path):
        return jsonify({'error': '视频文件不存在'}), 404

    # 生成唯一输出文件名
    out_basename = f"clip_{uuid.uuid4().hex[:8]}_{filename}"
    output_path = os.path.join(RESULT_FOLDER, out_basename)

    # 临时片段文件列表
    temp_files = []
    try:
        for idx, seg in enumerate(segments):
            seg_start = float(seg['start'])
            seg_end = float(seg['end'])
            seg_duration = seg_end - seg_start
            if seg_duration <= 0:
                continue
            temp_file = os.path.join(RESULT_FOLDER, f"tmp_{uuid.uuid4().hex[:8]}_{idx}.mp4")
            # 关键点：-ss 放在 -i 前面，-t 放在 -i 后面，避免黑屏
            cmd = [
                'ffmpeg', '-y',
                '-ss', str(seg_start),
                '-i', input_path,
                '-t', str(seg_duration),
                '-c:v', 'libx264', '-c:a', 'aac', '-strict', 'experimental',
                '-movflags', '+faststart',
                temp_file
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if not os.path.exists(temp_file) or os.path.getsize(temp_file) < 1024:
                return jsonify({'error': f'剪辑片段失败: {result.stderr.decode("utf-8")[:300]}'})
            temp_files.append(temp_file)

        if not temp_files:
            return jsonify({'error': '无有效片段'}), 400

        # 生成 concat.txt
        concat_txt = os.path.join(RESULT_FOLDER, f"concat_{uuid.uuid4().hex[:8]}.txt")
        with open(concat_txt, 'w', encoding='utf-8') as f:
            for tf in temp_files:
                f.write(f"file '{os.path.abspath(tf).replace('\'', '\\\'')}'\n")

        # 合并片段，强制转码避免黑屏
        concat_cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_txt,
            '-c:v', 'libx264', '-c:a', 'aac', '-strict', 'experimental',
            '-movflags', '+faststart',
            output_path
        ]
        result = subprocess.run(concat_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if not os.path.exists(output_path) or os.path.getsize(output_path) < 1024:
            return jsonify({'error': f'合并片段失败: {result.stderr.decode("utf-8")[:300]}'})

        # 清理临时文件
        for tf in temp_files:
            if os.path.exists(tf):
                os.remove(tf)
        if os.path.exists(concat_txt):
            os.remove(concat_txt)

        return jsonify({'result_filename': out_basename})
    except Exception as e:
        # 清理
        for tf in temp_files:
            if os.path.exists(tf):
                os.remove(tf)
        if 'concat_txt' in locals() and os.path.exists(concat_txt):
            os.remove(concat_txt)
        return jsonify({'error': f'视频剪辑失败: {str(e)}'}), 500

@app.route('/api/separate', methods=['POST'])
def separate_audio():
    data = request.json
    filename = data.get('filename')
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    out_dir = os.path.join(RESULT_FOLDER, f'separate_{os.path.splitext(filename)[0]}')
    os.makedirs(out_dir, exist_ok=True)
    try:
        separator = Separator('spleeter:2stems')
        separator.separate_to_file(input_path, out_dir)
        # Spleeter输出到 out_dir/原文件名/vocals.wav 和 accompaniment.wav
        base = os.path.splitext(filename)[0]
        vocal_path = os.path.join(out_dir, base, 'vocals.wav')
        accomp_path = os.path.join(out_dir, base, 'accompaniment.wav')
        # 拷贝到 result 目录下便于下载
        vocal_out = os.path.join(RESULT_FOLDER, f'{base}_vocals.wav')
        accomp_out = os.path.join(RESULT_FOLDER, f'{base}_accompaniment.wav')
        import shutil
        shutil.copy(vocal_path, vocal_out)
        shutil.copy(accomp_path, accomp_out)
        return jsonify({
            'vocal': f'{base}_vocals.wav',
            'accompaniment': f'{base}_accompaniment.wav'
        })
    except Exception as e:
        return jsonify({'error': f'分离失败: {str(e)}'}), 500

@app.route('/api/asr', methods=['POST'])
def asr_audio():
    data = request.json
    filename = data.get('filename')
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(input_path):
        return jsonify({'error': 'File not found'}), 404
    try:
        model = whisper.load_model("base")  # 可选 tiny/base/small/medium/large
        result = model.transcribe(input_path)
        text = result.get('text', '')
        # 保存为txt
        txt_name = f"{os.path.splitext(filename)[0]}_asr.txt"
        txt_path = os.path.join(RESULT_FOLDER, txt_name)
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        return jsonify({'text': text, 'txt_filename': txt_name})
    except Exception as e:
        return jsonify({'error': f'语音识别失败: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)