from flask import request, abort, current_app, make_response, Response

from info import sr
from info.modules.passport import passport_blu
from info.utils.captcha.pic_captcha import captcha


@passport_blu.route('/get_img_code')
def get_img_code():
    # 获取参数
    img_code_id = request.args.get("img_code_id")
    # 校验参数
    if not img_code_id:
        return abort(403)
    # 生成图片验证码
    img_name, img_code_text, img_code_bytes = captcha.generate_captcha()
    # 将图片key和验证码文字保存到数据库中
    try:
        sr.set("img_code_id_" + img_code_id, img_code_text, ex=180)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(500)
    # 返回验证码图片
    # 创建响应头
    response = make_response(img_code_bytes)  # type: Response
    # 设置响应头
    response.content_type = "image/jpeg"
    return response
