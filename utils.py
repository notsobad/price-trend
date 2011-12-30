#coding=utf-8
import re
import urlparse
from urllib import unquote

G_loger = None

def log(msg):
	# setup the logging
	if not G_loger:
		logger = logging.getLogger('update')
		logger.setLevel(logging.DEBUG)
		handler = logging.StreamHandler(sys.stdout)
		formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
		handler.setFormatter(formatter)
		logger.addHandler(handler)
		G_logger = logger
	G_logger.info(msg)




def md5sum(file_name):
    f = open(file_name, 'rb')
    md5 = hashlib.md5()
    buffer = f.read(2 ** 20) 
    while buffer:
        md5.update(buffer)
        buffer = f.read(2 ** 20) 
    f.close()
    return md5.hexdigest()



def re_match(reg, text):
	#m = re.search(reg, text, re.MULTILINE)
	m = reg.search(text)
	if m:
		g = m.groups()
		#print g
		if len(g) == 1:
			return m.groups()[0]
		return g
	return ''



def unquote_u(source):
	result = source
	if '%u' in result:
		result = result.replace('%u','\\u').decode('unicode_escape')
	result = unquote(result)
	return result


