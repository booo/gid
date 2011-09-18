from restkit import Resource
import urllib

class RestResource(Resource):

    def getWithCookies(self, path, reqCookies = None):
        reqHeaders = {}
        if reqCookies:
          reqHeaders['Cookie'] = RestResource._cookiesToStr(reqCookies)

        response = self.get(path, headers = reqHeaders)

        return response.body_string(), self._getCookiesFromHeader(response.headers)


    def deleteWithCookie(self, path, cookies = None):
        reqHeaders = {}
        if reqCookies:
          reqHeaders['Cookie'] = RestResource._cookiesToStr(reqCookies)

        response = self.delete(path, headers = reqHeaders)

        return response.body_string(), self._getCookiesFromHeader(response.headers)


    def postForm(self, path, data, reqCookies = None):
        reqPayload = '&'.join(
            [ '='.join( [k, urllib.quote(v)] ) for k,v in data.items() ]
          )

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
        

        return response.body_string(), self._getCookiesFromHeader(response.headers)

    
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
