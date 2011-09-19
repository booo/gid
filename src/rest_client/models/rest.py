from restkit import Resource
import urllib

class RestResource(Resource):

    def getWithCookies(self, path, reqCookies = None):
        reqHeaders = {}
        if reqCookies:
          reqHeaders['Cookie'] = RestResource._cookiesToStr(reqCookies)

        response = self.get(path, headers = reqHeaders)

        return response.body_string()


    def deleteWithCookie(self, path, reqCookies = None):
        reqHeaders = {}
        if reqCookies:
          reqHeaders['Cookie'] = RestResource._cookiesToStr(reqCookies)

        response = self.delete(path, headers = reqHeaders)

        return response.body_string()


    def postForm(self, path, data, reqCookies = None):
        reqPayload = RestResource._payloadToStr(data)

        reqHeaders = {
            'Content-Type' : 'application/x-www-form-urlencoded',
          }

        if reqCookies:
          reqHeaders['Cookie'] = RestResource._cookiesToStr(reqCookies)


        response = self.post(
              path,
              headers=reqHeaders,
              payload=reqPayload
            )
        

        return response.body_string()


    def putForm(self, path, data, reqCookies = None):
        reqPayload = RestResource._payloadToStr(data)

        reqHeaders = {
            'Content-Type' : 'application/x-www-form-urlencoded',
          }

        if reqCookies:
          reqHeaders['Cookie'] = RestResource._cookiesToStr(reqCookies)


        response = self.put(
              path,
              headers=reqHeaders,
              payload=reqPayload
            )
        

        return response.body_string()

    
    @staticmethod
    def _payloadToStr(data):
        return '&'.join(
            [ '='.join( [k, urllib.quote(str(v))] ) for k,v in data.items() ]
          )


    @staticmethod
    def _cookiesToStr(cookies):
        return ';'.join(
                  ['='.join([k,'"%s"'%v]) for k,v in cookies.items() ]
                )


    @staticmethod
    def _getCookiesFromHeader(headers):
        if 'Set-Cookie' not in headers:
          return {}

        cookies = headers['Set-Cookie'][:headers['Set-Cookie'].rindex('; Path')]

        f = lambda x : tuple([s.strip('"') for s in x.split('=', 1)])

        if '&' not in cookies:
            data = [f(cookies)]

        else:
            data = map(f, cookies.split('&'))

        return dict(data)
