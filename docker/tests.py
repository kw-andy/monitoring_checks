import re

from src import cabourotte_autoconfig


webservices = cabourotte_autoconfig.webservices_list()
healthchecks = cabourotte_autoconfig.healthchecks_list()

'''
#test case 1 - less than 3 elements per sublist
case1 = ['boo','boo','boo.com'],['baa','baa','baa.com'],['bzz','bzzcom']  
#test case 2 - not dot on the third element in any sublist
case2 = ['boo','boo','boo.com'],['baa','baa','baa.com'],['bzz','bzz','bzzcom'] 

'''

def test_check_weblist_three_elems_plus_dot(webservices):
    #only output
    assert all(isinstance(item, list) and len(item) == 3 for item in webservices)
    assert all(re.findall("[.]", item[2]) for item in webservices)


'''
#test case 1 - less than 2 elements per sublist
case1 = ['boo','boo.com'],['baa','baa.com'],['bzz']  
#test case 2 - not dot on the second element in any sublist
case2 = ['boo','boo.com'],['baa','baa.com'],['bzz','bzzcom'] 

'''

def test_check_healthchecks_two_elems_plus_dot(healthchecks):
    #only output
    assert all(isinstance(item, list) and len(item) == 2 for item in healthchecks)
    assert all(re.findall("[.]", item[1]) for item in healthchecks)

'''

in_mockweb = ['boo','boo.com'],['baa','baa.com'],['bzz']  
in_mockhealth = ['boo','boo.com'],['baa','baa.com'],['bzz','bzzcom'] 

out_mockweb = ['boo','boo','boo.com'],['baa','baa','baa.com'],['bzz','bzz','bzz.com']  
out_mockhealth = ['bii','bii.com'],['brr','brr.com'],['bdd','bdd.com']

'''    

def test_check_add_h(in_mockweb, in_mockhealth,out_mockweb,out_mockhealth):
    #input
    assert all(isinstance(item, list) and len(item) == 2 for item in in_mockhealth)
    assert all(isinstance(item, list) and len(item) == 3 for item in in_mockweb)
    assert all(re.findall("[.]", item[2]) for item in in_mockweb)
    assert all(re.findall("[.]", item[1]) for item in in_mockhealth)
    #output
    results = cabourotte_autoconfig.add_healthcheck(out_mockweb, out_mockhealth,ah_filename)
    assert '4' not in results,"pass"
    assert '5' not in results,"pass"

def test_check_rem_h(in_mockweb, in_mockhealth,out_mockweb,out_mockhealth):
    #input
    assert all(isinstance(item, list) and len(item) == 2 for item in in_mockhealth)
    assert all(isinstance(item, list) and len(item) == 3 for item in in_mockweb)    
    assert all(re.findall("[.]", item[2]) for item in in_mockweb)
    assert all(re.findall("[.]", item[1]) for item in in_mockhealth)
    #output
    results = cabourotte_autoconfig.remove_healthcheck(out_mockweb, out_mockhealth,ah_filename)
    assert '4' not in results,"pass"
    assert '5' not in results,"pass"


