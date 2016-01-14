# this is an example for retrieve page from sina.com
# to run this example, double click icon pyLab and input following command
# run d:\getFinanceSina.py
#
import requests;
import re;

url = 'http://money.finance.sina.com.cn/corp/go.php/vFD_FinanceSummary/stockid/300159.phtml'
resp = requests.get(url)
resp.encoding='gbk';

patPeriod = re.compile(ur"<a name=\"(.*)\"><\/a><strong>截止日期")
patItem = re.compile(ur">(每\W*)</td>")
patFinance = re.compile(ur">(\-?\d*\.{1}\d*)元<")
lines = resp.text.split('\n')
for line in lines:
	res = patPeriod.search(line)
	if res != None:
		print res.group(1)
	res = patItem.search(line)
	if res != None:
		print res.group(1)
	res = patFinance.search(line)
	if res != None:
		print res.group(1)



