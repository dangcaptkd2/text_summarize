# -*- coding: utf-8 -*-
import logging

class RequestForm:
    def __init__(self, request):
        self.__get = dict()
        self.__post = dict()

        if request.args is not None:
            for K in request.args:
                self.__get[K] = request.args.get(K)
        if request.form is not None:
            for K in request.form:
                self.__post[K] = request.form.get(K)
        obj = request.get_json(silent=True)
        if obj is not None:
            for K in obj:
                self.__post[K] = obj.get(K)
        # print("self.__get", self.__get)
        # print("self.__post", self.__post)

    def get_val(self, key, default, method="get"):
        try:
            val = None
            method = method.lower()
            # print("key, default, method", key, default, method)
            if method == "get":
                if key in self.__get:
                    val = self.__get.get(key)
            elif method == "post":
                if key in self.__post:
                    val = self.__post.get(key)
            if val is None:
                val = default
            return val
        except Exception as e:
            logging.error(str(e), exc_info=True)
            return default

    def get_list_str(self, key, default, method="get"):
        list_str = []
        key_arr = f"{key}["
        for K in self.__post.keys():
            if K.startswith(key_arr):
                list_str.append(self.__post.get(K))
        return list_str

    def get_str(self, key, default, method="get"):
        val = self.get_val(key, default, method)
        if val is None:
            return default
        return val

    def get_int(self, key, default, method="get"):
        try:
            val = self.get_val(key, default, method)
            if val is None:
                return default
            return int(val)
        except Exception as e:
            logging.error(str(e), exc_info=True)
            return default

    def __str__(self) -> str:
        return f"(get={self.__get}, post={self.__post})"


def get_param(key, default=None, method="get"):
    method = method.lower()
    # print("request.args", request.args)
    # print("request.form", request.form)
    # print("---> method", method)
    # est.get_json {'title': 'Tình tay ba của người đàn bà xảo quyệt', 'content': 'Tòa lương tâm bạn ơi.', 'lead': 'Sharee Miller mượn tay tình nhân để thủ tiêu chồng nhằm chiếm tiền bảo hiểm, nhưng sau đó cô ta lật mặt khiến người tình đau khổ mà tự sát.', 'cat': 'phap luat'}
    # print('request.get_json', request.get_json(silent=True))

    if method == "get":
        if key in request.args:
            # print("--> request.args", request.args)
            return request.args.get(key)
    elif method == "post":
        obj = request.get_json(silent=True)
        if obj is not None:
            if key in obj:
                return request.form.get(key)
        if key in request.form:
            # print("--> request.form", request.form)
            return request.form.get(key)
    elif method == "json":
        try:
            data = request.get_json()
            if key in data:
                return data.get(key)
        except:
            return default
    return default


# if __name__ == "__main__":
#     from http_server.controllers import *