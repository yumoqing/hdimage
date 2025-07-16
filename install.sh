
curdir=$(pwd)
echo $curdir
python3 -m venv $curdir/py3
# $curdir/py3/bin/pip install git+https://github.com/HiDream-ai/HiDream-I1.git
$curdir/py3/bin/pip install -U flash-attn --no-build-isolation
# $curdir/py3/bin/pip install git+https://github.com/huggingface/diffusers.git
$curdir/py3/bin/pip install git+https://git.kaiyuancloud.cn/yumoqing/apppublic
$curdir/py3/bin/pip install git+https://git.kaiyuancloud.cn/yumoqing/sqlor
$curdir/py3/bin/pip install git+https://git.kaiyuancloud.cn/yumoqing/ahserver
$curdir/py3/bin/pip install packaging
$curdir/py3/bin/pip install wheel
$curdir/py3/bin/pip install SentencePiece
$curdir/py3/bin/pip install flash-attn
