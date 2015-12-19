import datetime
import http.client
import urllib.parse
import ssl

class sms(object):
    def __init__(self, username, password, host='https://sms.stadel.dk/send.php', ssl_context=None):
        """Create a new SMS sender"""
        self.srv = {
                'username': username,
                'password': password,
                'host': urllib.parse.urlparse(host)
                }

        self.opt = {
                'url_ok': None,
                'url_error': None,
                'time': None,
                'flash': False,
                }

        if self.srv['host'].scheme == 'http':
            self.http = http.client.HTTPConnection(self.srv['host'].netloc)
        elif self.srv['host'].scheme == 'https':
            self.http = http.client.HTTPSConnection(self.srv['host'].netloc, context=ssl_context)
        else:
            raise http.client.UnknownProtocol()

    def set_url_ok(self, url):
        self.opt['url_ok'] = url

    def set_url_err(self, url):
        self.opt['url_error'] = url

    def set_time(self, time):
        if type(time) == datetime.datetime:
            self.opt['time'] = time
        else:
            raise TypeError('Time must be of datetime.datetime type.')

    def set_flash(self, boolean):
        if type(boolean) == bool:
            self.opt['flash'] = boolean
        else:
            raise TypeError('Boolean must be of bool type.')

    def __merge_parms(self):
        parms = {}
        if self.opt['url_ok'] is not None:
            parms['url_ok'] = self.opt['url_ok']

        if self.opt['url_error'] is not None:
            parms['url_error'] = self.opt['url_error']

        if self.opt['time'] is not None:
            parms['time'] = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}".format(
                    #2008-12-14 20:30
                    self.opt['time'].year,
                    self.opt['time'].month,
                    self.opt['time'].day,
                    self.opt['time'].hour,
                    self.opt['time'].minute,
                    )

        if self.opt['flash']:
            parms['flash'] = '1'

        parms['user'] = self.srv['username']
        parms['pass'] = self.srv['password']
    
        print(parms)

        return parms


    def send(self, msg, mobile=None, group=None, sender=None):
        parms = self.__merge_parms()
        if mobile is None and group is None:
            raise Exception('Neither group or mobile given')
        if mobile is not None and group is not None:
            raise Exception('Bouth group and mobile given')

        parms['message'] = msg
        if mobile is not None:
            parms['mobile'] = mobile
        if group is not None:
            parms['group'] = group
        
        headers = {"Content-type": "application/x-www-form-urlencoded",
                "Accept": "text/plain"}

        post = urllib.parse.urlencode(parms)

        self.http.request("POST", self.srv['host'].path, post, headers)
        response = self.http.getresponse()
        
        return self.__response(response.status, response.reason, response.read())

    def __response(self, status, reason, data):
        if status != 200:
            raise Exception('Expected status code 200 from HTTP(s) server, got: {} {}'.format(status, reason))
        text = data.decode('utf-8').strip()
        parts = text.split('|')
        if len(parts) != 3:
            raise Exception('Expected 3part text from server, got: "{}"'.format(text))
        if parts[0] == 'ERROR':
            raise Exception('Got error from server: {}'.format(parts[2]))
        if parts[0] == 'OK':
            return True

    def close(self):
        self.http.close()



# https://sms.stadel.dk/send.php




