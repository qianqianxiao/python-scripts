# coding:utf8
import json
from django.conf import settings
import redis
import requests


__author__ = 'yoyo.Chen'


class WechatException(Exception):
    pass


class WechatApi(object):
    def __init__(self):
        self.appid = 'WEIXIN APPIS'
        self.secret = 'WEIXIN SECRET'

    @staticmethod
    def _check_error(res):
        if "errcode" in res:
            if res["errcode"] != 0 and res["errcode"] not in [40001, 40003]:
                error_msg = res["errmsg"].encode('utf8')
                raise WechatException(error_msg)
        return res

    def _transcoding(self, data):
        """
        编码转换
        :param data: 需要转换的数据
        :return: 转换好的数据
        """
        if not data:
            return data
        result = None
        if isinstance(data, str):
            result = data.decode('utf-8')
        else:
            result = data
        return result

    def _transcoding_list(self, data):
        """
        编码转换 for list
        :param data: 需要转换的 list 数据
        :return: 转换好的 list
        """
        if not isinstance(data, list):
            raise ValueError('Parameter data must be list object.')

        result = []
        for item in data:
            if isinstance(item, dict):
                result.append(self._transcoding_dict(item))
            elif isinstance(item, list):
                result.append(self._transcoding_list(item))
            else:
                result.append(item)
        return result

    def _transcoding_dict(self, data):
        """
        编码转换 for dict
        :param data: 需要转换的 dict 数据
        :return: 转换好的 dict
        """
        if not isinstance(data, dict):
            raise ValueError('Parameter data must be dict object.')

        result = {}
        for k, v in data.items():
            k = self._transcoding(k)
            if isinstance(v, dict):
                v = self._transcoding_dict(v)
            elif isinstance(v, list):
                v = self._transcoding_list(v)
            else:
                v = self._transcoding(v)
            result.update({k: v})
        return result

    def _post(self, url, **kwargs):
        """
        使用 POST 方法向微信服务器发出请求
        :param url: 请求地址
        :param kwargs: 附加数据
        :return: 微信服务器响应的 json 数据
        :raise HTTPError: 微信api http 请求失败
        """
        return self._request(
            method="post",
            url=url,
            **kwargs
        )

    def _request(self, method, url, **kwargs):
        """
        向微信服务器发送请求
        :param method: 请求方法
        :param url: 请求地址
        :param kwargs: 附加数据
        :return: 微信服务器响应的 json 数据
        :raise HTTPError: 微信api http 请求失败
        """
        access_token = self.check_access_token()
        if "params" not in kwargs:
            kwargs["params"] = {
                "access_token": access_token,
            }
        if isinstance(kwargs.get("data", ""), dict):
            body = json.dumps(kwargs["data"], ensure_ascii=False)
            body = body.encode('utf8')
            kwargs["data"] = body

        r = requests.request(
            method=method,
            url=url,
            **kwargs
        )
        r.raise_for_status()
        response_json = r.json()
        return response_json

    def check_access_token(self):
        """
        检测并获取access_token
        """
        redis_conn = redis.Redis.from_url('REDIS_URL')
        access_token = redis_conn.get(redis_key)
        if not access_token:
            access_url = 'https://api.weixin.qq.com/cgi-bin/token?'
            appid = self.appid
            secret = self.secret
            grant_type = 'client_credential'
            payload = {
                'appid': appid,
                'secret': secret,
                'grant_type': grant_type,
            }
            r = requests.get(access_url, params=payload, verify=False)
            res = json.loads(r.text)
            access_token = res.get('access_token')
            expires_in = int(int(res.get('expires_in')) - 3600)
            redis_conn.set(redis_key, access_token)
            redis_conn.expire(redis_key, expires_in)
        return access_token

    def send_templates_msg(self, open_id, template_id, url, data, topcolor="#FF0000"):
        """
        微信发送模版消息
        """
        unicode_data = {}
        if data:
            unicode_data = self._transcoding_dict(data)
        return self._post(
            url='https://api.weixin.qq.com/cgi-bin/message/template/send',
            data={
                'touser': open_id,
                "template_id": template_id,
                "url": url,
                "topcolor": topcolor,
                "data": unicode_data
            }
        )

    def wechat_user_info(self, open_id):
        """
        获取用户信息
        """
        access_token = self.check_access_token()
        access_url = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token={0}&openid={1}'.format(access_token, open_id)
        r = requests.get(access_url, verify=False)
        res = json.loads(r.text)
        return res

if __name__ == '__main__':
    data = {
        "first": {
            "value": "您好，很抱歉通知您，您乘坐的航班发生延误！",
            "color": "#173177"
        },
        "trainNumber": {
            "value": "T1823",
            "color": "#173177"
        },
        "airline": {
            "value": "上海浦东→北京首都",
            "color": "#173177"
        },
        "formerTime": {
            "value": "2013年10月03日 19:00",
            "color": "#173177"
        },
        "departureTime": {
            "value": "2013年10月03日 19:40",
            "color": "#173177"
        },
        "remark": {
            "value": "敬请留意我们的微信通知，注意航班变化。",
            "color": "#173177"
        }
    }

    data = {
        "first": {
            "value": "尊敬的旅客,你关注的航班状态信息",
            "color": "#173177"
        },
        "FlightData": {
            "value": "3月2日",
            "color": "#173177"
        },
        "FlightNo": {
            "value": "T1823",
            "color": "#173177"
        },
        "DepCity": {
            "value": "上海",
            "color": "#173177"
        },
        "DepTime": {
            "value": "19:40",
            "color": "#173177"
        },
        "ArrCity": {
            "value": "北京",
            "color": "#173177"
        },
        "ArrTime": {
            "value": "21:40",
            "color": "#173177"
        },
        "remark": {
            "value": "敬请留意我们的微信通知，注意航班变化。",
            "color": "#173177"
        }
    }
    test = "#173177"
    data = {
        "first": {
            "value": "您好，很抱歉通知您，您乘坐的航班因故取消",
            "color": "#173177"
        },
        "trainNumber": {
            "value": "T1823",
            "color": "#173177"
        },
        "airline": {
            "value": "上海浦东→北京首都",
            "color": "#173177"
        },
        "remark": {
            "value": "建议您改期或者进行退票。",
            "color": test
        }
    }
    test = WechatApi()
    print test.send_templates_msg('XXXXXX',
                                  'XXXXXXX',
                                  url="http://www.baidu.com",
                                  data=data,
                                  topcolor="#FF0000")

    print test.wechat_user_info('XXXXXXX')
