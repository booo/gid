from restkit import Resource, BasicAuth, ResourceNotFound

import urllib

class RestResource(Resource):

    def basicAuth(username, password):
        return BasicAuth(username, password)

    def getWithAuth(self, username, password, path = None):
        reqHeaders = {}

        self.client.filters.append(BasicAuth(username, password))
        self.client.load_filters()

        if path == None:
            response = self.get(headers = reqHeaders)
        else:
            response = self.get(path, headers = reqHeaders)

        return response.body_string()


    def deleteWithAuth(self, username, password, path = None):
        reqHeaders = {}

        self.client.filters.append(BasicAuth(username, password))
        self.client.load_filters()

        if path == None:
            response = self.delete(headers = reqHeaders)
        else:
            response = self.delete(path, headers = reqHeaders)

        return response.body_string()


    def postForm(self, data, path=None, username = None, password = None):
        reqPayload = RestResource._payloadToStr(data)

        reqHeaders = {
            'Content-Type' : 'application/x-www-form-urlencoded',
          }

        if username != None and password != None:
            self.client.filters.append(BasicAuth(username, password))
            self.client.load_filters()

        response = self.post(
              path,
              headers=reqHeaders,
              payload=reqPayload
            )


        return response.body_string()


    def putForm(self, data, path = None, username = None, password = None):
        reqPayload = RestResource._payloadToStr(data)

        reqHeaders = {
            'Content-Type' : 'application/x-www-form-urlencoded',
          }

        if username != None and password != None:
            self.client.filters.append(BasicAuth(username, password))
            self.client.load_filters()

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
