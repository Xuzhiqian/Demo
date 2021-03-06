# coding=utf-8
import os
import logging
import ffmpeg
import cv2
import random
from datasketch import MinHash
import numpy as np
import nltk
from nltk.corpus import wordnet as wn
from PIL import Image
from colorama import Fore, Style

# 设置log
logging.basicConfig(
    level=logging.INFO,
    format=''.join([Style.DIM, '[%(asctime)s] ',
                    Style.NORMAL, '%(message)s',
                    Style.RESET_ALL]),
    datefmt='%m-%d %T',
)
logging.getLogger("requests").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def cropImage(src, des, filename=None):
    """
    利用PIL随机剪切图片长宽的 0% - 25%
    :param src: source picture file path
    :param des: destination picture store directory path
    :param filename: destination picture file name
    :return: bool, True for success
    """
    FIXED_RATIO = 0.25
    if os.path.isfile(src):
        im = Image.open(src)
        box = []
        for i in im.size:
            l = random.randint(0, int(i * FIXED_RATIO))
            a = random.randint(0, l)
            b = i - l + a
            box += [a, b]
        box[1], box[2] = box[2], box[1]
        crop = im.crop(box)
        if os.path.isdir(des):
            pass
        else:
            logger.warning(Fore.YELLOW + des + ': no such directory.')
            os.mkdir(des)
            logger.info(Fore.BLUE + 'os mkdir ' + des)
        if filename is None:
            filename = 'default_crop.jpeg'
            logger.warning(
                Fore.YELLOW + 'saved file has been set to default_crop.jpeg')
        try:
            crop.save(os.path.join(des, filename))
            logger.info(
                Fore.BLUE + 'cropped image range (left, upper, right, lower) {0}'.format(box))
        except Exception as exc:
            logger.error(
                Fore.RED + 'save {0} failed with error {1}'.format(os.path.join(des, filename), exc))
            return False
        return True
    else:
        logger.error(Fore.RED + src + ': no such file.')
        return False


def rotateImage(src, des, filename=None):
    """
    利用PIL随机旋转图片长宽的 0-45 度
    :param src: source picture file path
    :param des: destination picture store directory path
    :param filename: destination picture file name
    :return: None
    """
    FIXED_ROTATION = 45
    if os.path.isfile(src):
        im = Image.open(src)
        _degree = random.randint(0, FIXED_ROTATION)
        rotate = im.rotate(_degree)
        if os.path.isdir(des):
            pass
        else:
            logger.warning(Fore.YELLOW + des + ': no such directory.')
            os.mkdir(des)
            logger.info(Fore.BLUE + 'os mkdir ' + des)
        if filename is None:
            filename = 'default_rotate.jpeg'
            logger.warning(
                Fore.YELLOW + 'saved file has been set to default_rotate.jpeg')
        try:
            rotate.save(os.path.join(des, filename))
            logger.info(Fore.BLUE + 'rotated image {0} degree'.format(_degree))
        except Exception as exc:
            logger.error(
                Fore.RED + 'save {0} failed with error {1}'.format(os.path.join(des, filename), exc))
            return False
        return True
    else:
        logger.error(Fore.RED + src + ': no such file.')
        return False


def mergeImage(src, des, filename=None):
    """
    利用PIL横向合并图片，对于不同大小的图片，先将大图片压缩至最小图片的尺度，再合并
    :param src: list, source picture file path list
    :param des: destination picture store directory path
    :param filename: destination picture file name
    :return: None
    """
    for i in src:
        if not os.path.isfile(i):
            logger.error(Fore.RED + i + ': no such file.')
            return False
    # https://stackoverflow.com/questions/30227466/combine-several-images-horizontally-with-python
    imgs = [Image.open(i) for i in src]
    # pick the image which is the smallest, and resize the others to match it (can be arbitrary image shape here)
    min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]
    imgs_comb = np.hstack((np.asarray(i.resize(min_shape)) for i in imgs))
    imgs_comb = Image.fromarray(imgs_comb)
    if os.path.isdir(des):
        pass
    else:
        logger.warning(Fore.YELLOW + des + ': no such directory.')
        os.mkdir(des)
        logger.info(Fore.BLUE + 'os mkdir ' + des)
    if filename is None:
        filename = 'default_merge.jpeg'
        logger.warning(
            Fore.YELLOW + 'saved file has been set to default_merge.jpeg')
    try:
        imgs_comb.save(os.path.join(des, filename))
        logger.info(Fore.BLUE + 'merged image {0} size'.format(min_shape))
    except Exception as exc:
        logger.error(
            Fore.RED + 'save {0} failed with error {1}'.format(os.path.join(des, filename), exc))
        return False
    return True


def SIFT(src):
    """
    利用cv2图片SIFT获得特征
    :param src: source picture file path
    :return: keypoint and descriptor
    """
    if os.path.isfile(src):
        img = cv2.imread(os.path.abspath(src), cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        sift = cv2.xfeatures2d.SIFT_create()
        kp, des = sift.detectAndCompute(gray, None)
        return kp, des
    else:
        logger.error(Fore.RED + src + ': no such file.')


def getVideoInfo(src):
    """
    利用FFmpeg获取视频文件信息
    :param src: source video file path
    :return: dict ffmpeg video stream info
    """
    if os.path.isfile(src):
        probe = ffmpeg.probe(src)
        video_stream = next(
            (stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        return video_stream
    else:
        logger.error(Fore.RED + src + ': no such file.')


def keyFrameExtraction(src, des):
    """
    利用FFmpeg进行关键帧提取
    :param src: source video file path
    :param des: destination keyframe store directory path
    :return: bool, True for success
    """
    if os.path.isfile(src):
        _input = ffmpeg.input(src)
        _filter = _input.filter('select', 'eq(pict_type,PICT_TYPE_I)')
        if os.path.isdir(des):
            pass
        else:
            logger.warning(Fore.YELLOW + des + ': no such directory.')
            os.mkdir(des)
            logger.info(Fore.BLUE + 'os mkdir ' + des)
        _output = _filter.output(os.path.join(
            des, 'keyframe_%02d.jpeg'), format='image2', vsync=2)
        _out, _err = _output.run()
        if _err:
            logger.error(Fore.RED + 'ffmpeg error: ' + _err)
            return False
        return True
    else:
        logger.error(Fore.RED + src + ': no such file.')
        return False


def cutVideo(src, des, filename=None, start_timestamp=0, duration=10):
    """
    利用FFmpeg进行视频切割
    :param src: source video file path
    :param des: destination keyframe store directory path
    :param filename: output file name
    :param start_timestamp: start to crop video
    :param duration: output video length, should more than 10 seconds
    :return: bool, True for success
    """
    if os.path.isfile(src):
        _input = ffmpeg.input(src)
        if os.path.isdir(des):
            pass
        else:
            logger.warning(Fore.YELLOW + des + ': no such directory.')
            os.mkdir(des)
            logger.info(Fore.BLUE + 'os mkdir ' + des)
        if filename is None:
            filename = 'default_crop.mp4'
            logger.warning(
                Fore.YELLOW + 'saved file has been set to default_crop.mp4')
        _output = _input.output(os.path.join(
            des, filename), ss=start_timestamp, t=duration, c='copy')
        _out, _err = _output.run()
        if _err:
            logger.error(Fore.RED + 'ffmpeg error: ' + _err)
            return False
        return True
    else:
        logger.error(Fore.RED + src + ': no such file.')
        return False


def mergeVideo(src1, src2, des, filename=None):
    """
    利用FFmpeg进行两个视频的合并
    :param src1: source video file path
    :param src2: source video file path
    :param des: destination keyframe store directory path
    :param filename: output file name
    :return: bool, True for success
    """
    if os.path.isfile(src1) and os.path.isfile(src2):
        _input1 = ffmpeg.input(src1)
        _input2 = ffmpeg.input(src2)
        if os.path.isdir(des):
            pass
        else:
            logger.warning(Fore.YELLOW + des + ': no such directory.')
            os.mkdir(des)
            logger.info(Fore.BLUE + 'os mkdir ' + des)
        if filename is None:
            filename = 'default_merge.mp4'
            logger.warning(
                Fore.YELLOW + 'saved file has been set to default_merge.mp4')
        _joined = ffmpeg.concat(
            _input1['v'], _input1['a'], _input2['v'], _input2['a'], v=1, a=1)
        _output = _joined.output(os.path.join(des, filename))
        _out, _err = _output.run()
        if _err:
            logger.error(Fore.RED + 'ffmpeg error: ' + _err)
            return False
        return True
    else:
        logger.error(Fore.RED + src1 + 'or' + 'src2' + ': no such file.')
        return False


def getImageHashValues(sift_des):
    """
    利用datasketch得到图片的Hash值
    :param sift_des: OpenCV SIFT 后得到的des值，它应该是[n, 128]的向量
    :return: numpy.ndarray datasketch 计算得到的Hash值
    """
    assert type(
        sift_des) == np.ndarray, 'INPUT sift_des should be numpy.ndarray!'
    m = MinHash()
    for i in sift_des:
        assert type(
            i) == np.ndarray, 'INPUT sift_des[i] should be numpy.ndarray!'
        m.update(i.tostring())
    return m.hashvalues


def getImageJaccardMeasure(sift_des1, sift_des2):
    return None


def jaccardMeasure(hashvalue1, hashvalue2):
    """
    利用datasketch计算两个Hash值的Jaccard相似度
    :param hashvalue1: datasketch 哈希值1
    :param hashvalue2: datasketch 哈希值2
    :return: float 两个哈希值的相似度 [0, 1]
    """
    try:
        m1 = MinHash(hashvalues=hashvalue1)
        m2 = MinHash(hashvalues=hashvalue2)
        return m1.jaccard(m2)
    except Exception as exc:
        logger.error(Fore.RED + 'MinHash failed with {0}'.format(exc))
        return 0.0


def getTextHashValues(text, ngram=5):
    """
    利用datasketch和NLTK得到文本的Hash值
    :param text: 一段字符串文本
    :param ngram: n-gram的值，短文本推荐为5
    :return: numpy.ndarray datasketch 计算得到的Hash值
    """
    assert type(text) == str, 'INPUT text should be str'
    m = MinHash()
    for i in nltk.ngrams(text, ngram):
        m.update(''.join(i).encode('utf8'))
    return m.hashvalues


def removeSentences(text, num=2):
    """
    利用NLTK分句，随机删除一部分句子
    :param text: str, 输入文本
    :param num: int, 删除句子的数量
    :return: str 处理后的文本
    """
    assert type(text) == str, 'INPUT text should be str'
    sen = nltk.sent_tokenize(text)
    l = len(sen)
    assert l > num, 'INPUT sentences are too less to remove'
    mask = np.ones(l)
    mask[:num] = 0
    mask = np.random.permutation(mask)
    logger.info(Fore.BLUE + 'Delete {0} sentence(s): '.format(
        l - sum(mask)) + ' $-$ '.join([sen[i] for i in range(l) if mask[i] == 0]))
    return ' '.join([sen[i] for i in range(l) if mask[i] == 1])


def removeWords(text, fraction=0.1):
    """
    利用NLTK分词，随机删除一部分单词
    :param text: str, 输入文本
    :param fraction: float, 删除单词的数量比例
    :return: str 处理后的文本
    """
    assert type(text) == str, 'INPUT text should be str'
    words = nltk.word_tokenize(text)
    l = len(words)
    mask = np.ones(l)
    mask[:int(l * fraction)] = 0
    mask = np.random.permutation(mask)
    logger.info(Fore.BLUE + 'Delete {0} word(s): '.format(
        l - sum(mask)) + ' , '.join([words[i] for i in range(l) if mask[i] == 0]))
    return ' '.join([words[i] for i in range(l) if mask[i] == 1])


def penn_to_wn(tag):
    """将tag词性和语义转换一下"""
    if tag.startswith('J'):
        return wn.ADJ
    elif tag.startswith('N'):
        return wn.NOUN
    elif tag.startswith('R'):
        return wn.ADV
    elif tag.startswith('V'):
        return wn.VERB
    return None


def pos_tag_with_synset(tagged):
    """将词性标签的tag转换为语义标签的tag
    :param tagged: nltk.pos_tag 的返回结果
    :return: tuple list, 语义标签
    """
    synsets = []
    lemmatzr = nltk.stem.WordNetLemmatizer()
    for token in tagged:
        wn_tag = penn_to_wn(token[1])
        if not wn_tag:
            synsets.append((token[0], None))  # 没有对应的语义
            continue
        lemma = lemmatzr.lemmatize(token[0], pos=wn_tag)
        syn = wn.synsets(lemma, pos=wn_tag)
        if(len(syn) > 0):
            synsets.append((token[0], syn[0]))  # 选择词性约束下的第一个语义
        else:
            synn = wn.synsets(lemma)
            if(len(synn) > 0):
                synsets.append((token[0], synn[0]))
            else:
                synsets.append((token[0], None))
    return synsets


def switchAntonyms(text, fraction=0.1):
    """
    利用NLTK分词，随机替换一部分词为反义词
    :param text: str, 输入文本
    :param fraction: float, 替换单词的数量比例，由于某些词没有反义词所以实际数量会比设定的要少
    :return: str 处理后的文本
    """
    assert type(text) == str, 'INPUT text should be str'
    words = nltk.word_tokenize(text)
    l = len(words)
    mask = np.ones(l)
    mask[:int(l * fraction)] = 0
    mask = np.random.permutation(mask)
    synsets = pos_tag_with_synset(nltk.pos_tag(words))
    antsets = []
    count = 0
    for i in range(l):
        if(mask[i] == 0):
            if(synsets[i][1] is not None):
                syn = synsets[i][1]
                if(syn.lemmas()):
                    flag = False
                    for j in syn.lemmas():
                        if j.antonyms():
                            # 选取排名第一个的反义词
                            antsets.append(j.antonyms()[0].name())
                            count += 1
                            flag = True
                            break
                    if(not flag):
                        antsets.append(synsets[i][0])
                else:
                    antsets.append(synsets[i][0])
            else:
                antsets.append(synsets[i][0])
        else:
            antsets.append(synsets[i][0])
    logger.info(Fore.BLUE + 'Switch {0} word(s): '.format(count))
    return ' '.join(antsets)
