from restkit import Resource
import urllib

class RestResource(Resource):

    def postForm(self, form, headers = None):
        reqPayload = '&'.join(
            [ '='.join( [k, urllib.quote(v)] ) for k,v in form.items() ]
          )

        reqHeaders = {
            'Content-Type' : 'application/x-www-form-urlencoded',
          }

        if headers:
          for k,v in headers.items():
            reqHeaders[k] = v

        response = self.post(
              '/',
              headers=reqHeaders,
              payload=reqPayload
            )

        cookies = dict(
                map(
                  lambda x : tuple(x.split('=', 1)),
                  response.headers['Set-Cookie'].split('&')[:-1]
                )
              )

        return response, cookies
