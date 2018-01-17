from django.shortcuts import render, redirect,render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post, Cross, Zen, Dry
import requests, json
import datetime
import xml.etree.ElementTree as ET
import requests
import sys
import copy

from mongoengine import connect
client = connect('mongo3', host='localhost', port=27017)


from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader

def search_author(request):
    return render(request, 'home/author.html')

def index(request):
    ''' To render Index page on application init '''
    print(datetime.datetime.now().strftime("%d/%m/%Y"))
    date = datetime.datetime.now().strftime("%d/%m/%Y")
    return render_to_response('home/index.html',
                 {'date': date })

def searchByAuthor(request):
    if 'author_name' in request.GET and request.GET['author_name']:
        page = request.GET.get('page', 1)

        t = loader.get_template('home/loading.html')

        author_name = request.GET['author_name']

        obj = Cross.objects.all()
        main_author = []
        for i in obj:
            for j in i.author:
                auth_obj = {
                'author_name':'',
                'doi': '',
                'title': '',
                'publisher': '',
                'issn': [],
                'funder': [],
                'reference': ''
                }
                try:
                    # print(str(j['given']+' ' +j['family']))
                    new_name = str(j['given']+' ' +j['family'])
                    finding_name = new_name.find(author_name)
                    if author_name in new_name:
                        auth_obj['author_name'] = new_name
                        auth_obj['doi'] = i.doi
                        auth_obj['title'] = i.title
                        auth_obj['publisher'] = i.publisher
                        auth_obj['issn'] = i.issn
                        
                        # print(new_name)
                        for au in i.funder:
                            funder_obj={
                                'funder_name': '',
                                'award': ''
                            }
                            try:
                                # au['name']
                                funder_obj['funder_name']=au['name']
                                # print(funder_obj)
                                funder_obj['award'] = ','.join(au['award'])
                            except(KeyError)as e:
                                pass
                            print(funder_obj)
                            auth_obj['funder'].append(funder_obj)
                        print(i.doi[:5])
                        ref_number = Post.objects.filter(reference__icontains=i.doi[:5]).first
                        try:
                            for re in ref_number.identifier:
                                if re is not None and 'doi:' in re:
                                    auth_obj['reference']=re
                                else:
                                    pass
                        except(KeyError, AttributeError)as e:
                            pass

                        main_author.append(auth_obj)
                    else:
                        pass
                except(KeyError, TypeError)as e:
                    pass

        post = Post.objects.all()
        for cr in post:
            for z in cr.creator:
                dry_auth_obj = {
                'author_name':'',
                'doi': '',
                'title': '',
                'reference':''
                }
                try:
                    if z is not None:
                        if author_name in z:
                            dry_auth_obj['author_name'] = z
                            dry_auth_obj['title'] = cr.title
                            dry_auth_obj['reference']=cr.reference
                            print(cr.reference)

                            for do in cr.identifier:
                                if do is not None and 'doi:' in do:
                                    dry_auth_obj['doi'] = do
                                else:
                                    pass
                            main_author.append(dry_auth_obj)
                        else:
                            pass

                except(KeyError)as e:
                    pass



            
        paginator = Paginator(main_author, 50) # Show 25 contacts per page
        word = paginator.page(page)
        # print(word)
        return render_to_response('home/author.html',
                 {'authors': word, 'query': author_name })
    else:
        return render(request, 'home/author.html')

def searchByPublisher(request):
    ''' 
        Searh by Publication
    '''
    if 'publisher_name' in request.GET and request.GET['publisher_name']:
        page = request.GET.get('page', 1)
        # print(page)

        publisher_name = request.GET['publisher_name']

        cross = Cross.objects.filter(publisher__icontains=publisher_name)
        main_publisher = []
        for c in cross:
            pub={
                'DOI':'',
                'name': '',
                'title': '',
                'funder':[],
                'award':[],
                'author': [],
                'source': 'Crossref',
                'reference': ''

            }
            pub['DOI'] = c.doi
            pub['name'] = c.publisher
            pub['title'] = c.title
            for i in c.funder:
                pub['funder'].append(i['name'])
                new_awards = ' '.join(i['award'])
                pub['award'].append(new_awards)
            for a in c.author:
                try:
                    pub['author'].append(a['given']+' '+a['family'])
                except(KeyError)as e:
                    pass

            ref = Post.objects.filter(reference__icontains=pub['DOI']).first()
            print(ref)
            if ref is not None:
                if ref.identifier is not None:
                    for k in ref.identifier:
                        if 'doi:' in k:
                            pub['reference'] = k
                        else:
                            pub['reference']='Null'
                else:
                    pass
            else:
                pass
            main_publisher.append(pub)
            # print(main_publisher)
        


        dryad = Post.objects.filter(publisher__icontains=publisher_name)
        for d in dryad:
            dy={
                'dry_doi':'',
                'name': '',
                'title':'',
                'creator': " ",
                'source': 'Dryad',
                'reference':''          
            }
            dy['name'] = d.publisher
            # print(dy['name'])
            dy['reference'] = d.reference
            dy['title'] = d.title
            for doi in d.identifier:
                if 'doi' in doi:
                    dy['dry_doi']=doi
                    # print(dy['dry_doi'])
            if d.creator is not None:
                dy['creator']=(''.join(d.creator))
            main_publisher.append(dy)
            # print(main_publisher)
            

        paginator = Paginator(main_publisher, 50) # Show 25 contacts per page
        try:
            word = paginator.page(page)
        except PageNotAnInteger:
        # If page is not an integer, deliver first page.
            word = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            word = paginator.page(paginator.num_pages)
        # print(word)
        return render_to_response('home/publisher.html',
                 {'cross': word, 'query': publisher_name })

    else:
        return render(request, 'home/publisher.html')

def search_publisher(request):
    return render(request, 'home/publisher.html')

def search_doi(request):
    return render(request, 'home/doi.html')

def searchByFunder(request):
    if 'funder_name' in request.GET and request.GET['funder_name']:
        page = request.GET.get('page', 1)

        award_name = request.GET['funder_name']
        # print(funder_name)

        funder = Cross.objects.all()
        main_funder = []
        for f in funder:
            fun={
                'name':'',
                'parent_doi': '',
                'doi': '',
                'award': '',
                'title': '',
                'refer_drayd':'',
                'source': 'Crossref',
                'author': []
            }
            for t in f.funder:
                if t['award'] is not None:
                    for aw in t['award']:
                        if award_name in aw:
                            try:
                                fun['name'] = t['name']
                            except(KeyError)as e:
                                fun['name'] = 'Null'

                            try:
                                fun['doi'] = t['DOI']
                            except(KeyError)as e:
                                fun['DOI']= 'Null'
                            try:
                                fun['award'] = ' , '.join(t['award'])
                            except(KeyError)as e:
                                fun['award'] = ''

                            if f.title is not None:
                                fun['title'] = f.title
                            else:
                                fun['title'] = 'Null' 

                            fun['parent_doi'] = f.doi

                            if f.author is not None: 
                                try:
                                    for au in f.author:
                                        fun['author'].append(au['given']+ ' ' +au['family'])
                                except(KeyError, Exception)as e:
                                    pass
                            else:
                                fun['author']=[]

                            print(fun['author'])

                            try:
                                post = Post.objects.filter(reference__icontains=t['DOI'][:5]).first()
                                if post.identifier is not None:
                                    for dr_id in post.identifier:
                                        if 'doi:' in dr_id:
                                            fun['refer_drayd'] = dr_id
                                            # print('In drayd reference')
                                        else:
                                            fun['refer_drayd']='Null'
                                else:
                                    fun['refer_drayd']='Null'
                            except (KeyError,AttributeError) as e:
                                pass
                            main_funder.append(fun)
                            # print(main_funder)
                        else:
                            pass
        paginator = Paginator(main_funder, 50) # Show 25 contacts per page

        try:
            word = paginator.page(page)
        except PageNotAnInteger:
            word = paginator.page(1)
        except EmptyPage:
            word = paginator.page(paginator.num_pages)

        return render_to_response('home/funder.html',
                 {'funders': word, 'query': award_name })
    else:
        return render(request, 'home/funder.html')


def search_keyword(request):
    return render(request, 'home/title.html')
def search_funder(request):
    return render(request, 'home/funder.html')

def post_dryad(request):
    get_data()
    # return render(request, 'home/index.html')
    return HttpResponseRedirect('/')

def post_crossref(request):
    save_cross()
    return HttpResponseRedirect('/')
#####################################################33333

def get_data():
    post = Post.objects.all()
    # post.delete()
    json_data = open('C:\\Users\\adminis\\Desktop\\Work\\Django\\Final_PROJECT\\new_django_mongo\\static\\Dyrad_ALL.json',encoding="utf8")
    # data = json.load(open('/static/b.json'))
    data = json.load(json_data)
    # data = json.load(open('Dyrad_TEN.json'))
    c=0
    for i in data:
        dry={
            'title': '',
            "creator": [],
            "description": '',
            "date": [],
            "type": '',
            "identifier": [],
            "relation": [],
            "publisher": '',
            "reference": '',
            "subjects": []
        }
        c+=1
        print(c)


        try:
            if i['metadata']['oai_dc:dc']['dc:title'] is not None:
                data_title = i['metadata']['oai_dc:dc']['dc:title']
                new_data_title = ''.join(data_title)
                dry['title'] = new_data_title
                print(dry['title'])
            else:
                dry['title']='Null'
        except(KeyError, TypeError) as e:
            # print('title', e)
            dry['title']='Null'



        try:
            if i['metadata']['oai_dc:dc']['dc:creator'] is not None:
                for cre in i['metadata']['oai_dc:dc']['dc:creator']:
                    dry['creator'].append(cre)
                print(dry['creator'])
            else:
                dry['creator']=[]
        except(KeyError, TypeError)as e:
            # print('creator', e)
            dry['creator']=[]



        try:
            if i['metadata']['oai_dc:dc']['dc:description'] is not None:
                dry['description'] = i['metadata']['oai_dc:dc']['dc:description']
            else:
                dry['description'] = 'Null'
        except(KeyError, TypeError)as e:
            # print('description', e)
            dry['description'] = 'Null'



        try:
            if i['metadata']['oai_dc:dc']['dc:date'] is not None:
                for da in i['metadata']['oai_dc:dc']['dc:date']:
                    if '$numberLong' in da:
                        print('')
                        continue
                    else:
                        dry['date'].append(da)
            else:
                dry['date']=[]
        except(KeyError, TypeError)as e:
            # print('date', e)
            dry['date']=[]



        try:
            if i['metadata']['oai_dc:dc']['dc:type'] is not None:
                type_data = (i['metadata']['oai_dc:dc']['dc:type'])
                type_new_data = ' '.join(type_data)
                dry['type'] = type_new_data
            else:
                dry['type'] = 'Null'
        except(KeyError, TypeError)as e:
            # print('type', e)
            dry['type'] = 'Null'



        try:
            if i['metadata']['oai_dc:dc']['dc:identifier'] is not None:
                for ide in i['metadata']['oai_dc:dc']['dc:identifier']:
                    # if '$numberLong' not in ide:
                    if 'doi:' in ide:
                        ref = get_reference(ide.split(':')[1])
                        if ref is not None:
                            new_ref = (ref.split('://doi.org/')[1])
                            if new_ref is not None:
                                dry['reference'] = new_ref
                                print(dry['reference'])
                            else:
                                dry['reference']='Null'
                        else:
                            dry['reference']='Null'
                    if '$numberLong' not in ide:
                        dry['identifier'].append(ide)
                    else:
                        continue
            else:
                dry['identifier'] = []
        except(KeyError, TypeError)as e:
            # print('identifier', e)
            dry['identifier']=[]


        try:
            if i['metadata']['oai_dc:dc']['dc:relation'] is not None:
                try:
                    relat=[]
                    for rel in i['metadata']['oai_dc:dc']['dc:relation']:
                        if '$numberLong' in rel:
                            print('')
                            dry['relation'].append('Null')
                        else:
                            relat.append(rel)
                    dry['relation'].append(''.join(relate))
                except(KeyError, TypeError)as e:
                    continue
            else:
                dry['relation'] = []
        except(KeyError, TypeError, Exception)as e:
            # print('relation', e)
            dry['relation'] = []



        try:
            if i['metadata']['oai_dc:dc']['dc:publisher'] is not None:
                dry['publisher'] = i['metadata']['oai_dc:dc']['dc:publisher']
                print('publisher',dry['publisher'])
            else:
                dry['publisher'] = 'Null'
                print('publisher',dry['publisher'])
        except(KeyError, TypeError, Exception)as e:
            # print('publisher', e)
            dry['publisher'] = 'Null'
            print('publisher',dry['publisher'])



        try:
            if i['metadata']['oai_dc:dc']['dc:subject'] is not None:
                try:
                    for sub in i['metadata']['oai_dc:dc']['dc:subject']:
                        if '$numberLong' in sub:
                            print('')
                            # dry['relation'].append('Null')
                            continue
                        else:
                            dry['subjects'].append(sub)
                except(KeyError, TypeError, Exception)as e:
                    continue
            else:
                dry['subjects'] = []
        except(KeyError,TypeError, Exception)as e:
            # print('subject', e)
            dry['subjects'] = []
        # c+=1
        print(c)
        # print(dry)

        post = Post(
            title=dry['title'], creator=dry['creator'],
            description=dry['description'], date=dry['date'],
            types=dry['type'], identifier=dry['identifier'],
            relation=dry['relation'], publisher=dry['publisher'],
            reference=dry['reference'], subjects=dry['subjects']
        )
        post.save()
        return 1
    return 1

def get_reference(doi):
  item = requests.get('https://datadryad.org/mn/object/http://dx.doi.org/{}'.format(doi))
  print('referense')
  root = ET.fromstring(item.text)
  for data in root:

      if data.tag[0] == "{":
          uri, ignore, tag = data.tag[1:].partition("}")
      else:
          tag = data.tag
      if tag == 'references':
          return data.text

#save_cross STARTS
def save_cross():
    cross = Cross.objects.all()
    cross.delete()
    json_data = open('C:\\Users\\adminis\\Desktop\\Work\\Django\\Final_PROJECT\\new_django_mongo\\static\\Cross_ALL.json',encoding="utf8")
    # data = json.load(open('/static/b.json'))
    data = json.load(json_data)
    c=0
    for i in data:
        items={
        'reference-count': '',
        'publisher': '',
        'funder':[],
        'DOI': '',
        'title': '',
        'reference': [],
        'author': [],
        'ISSN': [],
        'date-time': ''
        }
        c+=1

        try:
            if i['author'] is not None:
                for auth in i['author']:
                    items['author'].append(auth)
            else:
                items['author'] = []
        except(KeyError)as e:
          i['author']=[]



        try:
            if i['reference-count']['$numberLong'] is not None:
                items['reference-count'] = i['reference-count']['$numberLong']
            else:
                items['reference-count'] = 'Null'
        except(KeyError)as e:
            items['reference-count']=''


        try:
            if i['publisher'] is not None:
                items['publisher'] = i['publisher']
            else:
                items['publisher']='Null'
        except(KeyError)as e:
          items['publisher']='Null'


        try:
            if i['DOI'] is not None:
                items['DOI'] = i['DOI']
            else:
                items['DOI'] = 'Null'
        except(KeyError)as e:
            items['DOI'] = 'Null'


        try:
            if i['funder'] is not None:
                for fund in i['funder']:
                    items['funder'].append(fund)
            else:
                items['funder'] = []
        except(KeyError)as e:
          items['funder'] = []



        try:
            if i['title'] is not None:
                new_title = ' '.join(str(x) for x in i['title'])
                print(new_title)
                items['title'] = new_title
            else:
                items['title']=[]
        except(KeyError)as e:
            # print(e)
            continue



        try:
            if i['reference'] is not None:
                for ref in i['reference']:
                    items['reference'].append(ref)
            else:
                items['reference']=[]
        except (KeyError)as e:
            items['reference']=[]



        try:
            if i['ISSN'] is not None:
                for issn in i['ISSN']:
                    items['ISSN'].append(issn)
            else:
                items['ISSN']=[]
        except(KeyError)as e:
          items['ISSN']=[]




        try:
            if i['license'] is not None:
                for j in i['license']:
                    # items['date-time']=(j['start']['date-time'])
                    if j['start']['date-time'] is not None:
                        items['date-time']=(j['start']['date-time'])
                        break
                    else:
                        items['date-time'] = 'Null'
                        break
            else:
                items['date-time'] = 'Null'
        except(KeyError)as e:
          items['date-time'] = 'Null'



        cross = Cross(reference_count=items['reference-count'], publisher=items['publisher'], funder=items['funder'], doi=items['DOI'], title=items['title'], reference=items['reference'], author=items['author'], issn=items['ISSN'],date_time=items['date-time'])
        cross.save()
    return 1
#save_cross ENDS!

#################################zenodo function########################################
def post_zenodo(request):
    print('in zenodo')
    save_zenodo()
    return HttpResponseRedirect('/')

#save_zenodo starts here
def save_zenodo():
    zen = Zen.objects.all()

    json_data = open('C:\\Users\\adminis\\Desktop\\Work\\Django\\Final_PROJECT\\new_django_mongo\\static\\Zenodo.json',encoding="utf8")
    data = json.load(json_data)
    # print(data)
    c=0
    for i in data:


        zen_obj={
            'title': ' ',
            'creator': ' ',
            'conceptdoi': ' ',
            'doi': ' ',
            'related_identifiers' : [],
            'date': ' ',
            'links': []
        }

        try:
            if i['conceptdoi'] is not None:
                zen_obj['conceptdoi'] = i['conceptdoi']
                # print(zen_obj['conceptdoi'])
        except KeyError as e:
            zen_obj['conceptdoi']='Null'

        c=c+1

        try:
            if '$numberLong' not in i['doi']:
                zen_obj['doi'] = i['doi']
                # print(zen_obj['doi'])
        except(KeyError, Exception)as e:
            zen_obj['doi'] = 'Null'

        try:
            if i['metadata']['creators'] is not None:
                au=[]
                for a in i['metadata']['creators']:
                    if '$numberLong' not in a:
                        au.append(a['name'])
                    else:
                        continue
                zen_obj['creator'] = ', '.join(str(x) for x in au)
                # print(zen_obj['creator'])

        except(KeyError, Exception)as e:
            pass

        try:
            if i['metadata']['related_identifiers'] is not None:
                for ide in i['metadata']['related_identifiers'] :
                    if '$numberLong' not in ide:
                        zen_obj['related_identifiers'].append(ide)
                # print(zen_obj['related_identifiers'])
            else:
                zen_obj['related_identifiers'] = []
        except(KeyError, Exception)as e:
            zen_obj['related_identifiers'] = []


        try:
            if i['metadata']['publication_date'] is not None:
                if '$numberLong' not in i['metadata']['publication_date']:
                    zen_obj['date']=i['metadata']['publication_date']
                    # print(zen_obj['date'])
                else:
                    zen_obj['date']='Null'
            else:
                zen_obj['date']='Null'
        except(KeyError, Exception)as e:
            zen_obj['date']='Null'

        # return 1
        try:
            if i['metadata']['title'] is not None:
                zen_obj['title'] = i['metadata']['title']
                # print(zen_obj['title'])
            else:
                zen_obj['title'] = 'Null'
        except(KeyError, Exception)as e:
            zen_obj['title'] = 'Null'
        # print(zen_obj)

        # break
        url = {'conceptdoi': '', 'doi': ''}
        try:
            if i['links']['conceptdoi'] is not None:
                # print(i['links']['conceptdoi'])
                url['conceptdoi'] = i['links']['conceptdoi']


            if i['links']['doi'] is not None:
                # print(i['links']['doi'])
                url['doi'] = i['links']['doi']

            zen_obj['links'].append(url)

        except(KeyError, Exception)as e:
            print(e, 559)
            zen_obj['links'] = []

        # break
        # print(zen_obj)


        zen = Zen(title=zen_obj['title'], creator=zen_obj['creator'],
            conceptdoi=zen_obj['conceptdoi'], doi=zen_obj['doi'],
            related_identifiers=zen_obj['related_identifiers'],
            links=zen_obj['links']
        )
        zen.save()
        # return 1
        print(c)

    return 1
#save zenodo ends here

################################# search function########################################
def searchByDOI(request):
    '''
        Searh by DOI
    '''
    if 'doi_name' in request.GET and request.GET['doi_name']:
        page = request.GET.get('page',1)
        doi_name = request.GET['doi_name']
        # print(doi_name)
      
        cross = Cross.objects.filter(doi__icontains=doi_name)
        main_doi = []
        for c in cross:
            cross_doi_obj={
            'publisher': '',
            'funder': [],
            'doi': '',
            'title': '',
            'author': '',
            'issn':'',
            'source':'Crossref',
            'reference': ''
            }

            try:
                if c.publisher is not None:
                    cross_doi_obj['publisher'] = c.publisher
                    
                else:
                    cross_doi_obj['publisher'] = 'Null'
            except(KeyError, Exception)as e:
                pass

            try:
                if c.doi is not None:
                    cross_doi_obj['doi'] = c.doi
                else:
                    cross_doi_obj['doi']='Null'
            except(KeyError, Exception)as e:
                pass


            try:
                if c.title is not None:
                    cross_doi_obj['title'] = c.title
                else:
                    cross_doi_obj['title']= 'Null'
            except(KeyError, Exception)as e:
                pass

            try:
                if c.issn is not None:
                    cross_doi_obj['issn'] = ', '.join(str(x) for x in c.issn)
                    # print(cross_doi_obj['issn'])
                else:
                    cross_doi_obj['issn']=''
            except(KeyError, Exception)as e:
                pass

            try:
                if c.author is not None:
                    author_list=[]
                    for au in c.author:
                        author_list.append(au['given']+ ' ' + au['family'])
                    cross_doi_obj['author'] = ', '.join(author_list)
                    # print(cross_doi_obj['author'])
                else:
                    cross_doi_obj['author'] = 'Null'
            except(KeyError, Exception)as e:
                pass

            try:
                if c.funder is not None:
                    for fun in c.funder:
                        fun_obj={
                            'funder_name': '',
                            'award': ''
                        }
                        fun_obj['funder_name'] = fun['name']
                        award_obj=[]
                        for awa in fun['award']:
                            award_obj.append(awa)
                        fun_obj['award'] = ', '.join(award_obj)
                        cross_doi_obj['funder'].append(fun_obj)
            except(KeyError, Exception)as e:
                pass

            try:
                # print(cross_doi_obj[''])
                post = Post.objects.filter(reference__icontains=(c.doi[:5])).first()
                if post.identifier is not None:
                    for dr_id in post.identifier:
                        if 'doi:' in dr_id:
                            cross_doi_obj['reference'] = dr_id
                            # print('check',cross_doi_obj['reference'])
                        else:
                            pass
                else:
                    pass
            except (KeyError,TypeError,AttributeError) as e:
                pass

            main_doi.append(cross_doi_obj)


        dry_data = Post.objects.all()
        for d in dry_data:
            dry_data_obj={
            'title':'',
            'author':'',
            'publisher':'',
            'reference':'',
            'doi':'',
            'source': 'Dryad'
            }
            try:
                for ide in d.identifier:
                    if ide is not None and 'doi:' in ide:
                        if doi_name in ide:
                            # print(ide[4:])
                            dry_data_obj['doi'] = ide
                            # print(dry_data_obj['doi'])
                        # print(dry_data_obj['doi'])
                            if dry_data_obj['doi'] is not None:
                                try:
                                    if d.title is not None:
                                        dry_data_obj['title']= d.title
                                    else:
                                        pass
                                except(KeyError, Exception)as e:
                                    pass

                                try:
                                    if d.publisher is not None:
                                        dry_data_obj['publisher']= d.publisher
                                    else:
                                        pass
                                except(KeyError, Exception)as e:
                                    pass

                                try:
                                    if d.reference is not None:
                                        dry_data_obj['reference']= d.reference
                                    else:
                                        pass
                                except(KeyError, Exception)as e:
                                    pass

                                try:
                                    if d.creator is not None:
                                        dry_data_obj['author']=', '.join(str(x) for x in d.creator)
                                    else:
                                        pass
                                except(KeyError, Exception)as e:
                                    pass
                            main_doi.append(dry_data_obj)
                        else:
                            pass
                    else:
                        pass
            except(KeyError)as e:        
                pass

                
        zen_data = Zen.objects.filter(doi__icontains=doi_name)
        for z in zen_data:
            zen_data_obj={
            'title':'',
            'author':'',
            'doi':'',
            'source': 'Zenodo',
            'conceptdoi':'',
            'conceptdoi_link': '',
            'doi_link':'',
            'reference':''
            }

            try:
                if z.title is not None:
                    zen_data_obj['title']=z.title
                else:
                    pass
            except(KeyError, Exception)as e:
                pass

            try:
                if z.creator is not None:
                    zen_data_obj['author']= z.creator
                else:
                    pass
            except(KeyError, Exception)as e:
                pass

            try:
                if z.doi is not None:
                    zen_data_obj['doi']=z.doi
                else:
                    pass
            except(KeyError, Exception)as e:
                pass

            try:
                if z.conceptdoi is not None:
                    zen_data_obj['conceptdoi']=z.conceptdoi
                else:
                    pass
            except(KeyError, Exception)as e:
                pass

            try:
                if z.links is not None:
                    for lin in z.links:
                        # print(lin)
                        zen_data_obj['conceptdoi_link']=lin['conceptdoi']
                        zen_data_obj['doi_link']=lin['doi']
                        # print(zen_data_obj['conceptdoi_link'])
                else:
                    pass
            except(KeyError, Exception)as e:
                pass

            main_doi.append(zen_data_obj)
    

        paginator = Paginator(main_doi, 50)

        try:
            word = paginator.page(page)
        except PageNotAnInteger:
            word = paginator.page(1)
        except EmptyPage:
            word = paginator.page(paginator.num_pages)
        return render_to_response('home/doi.html',
                 {'cross': word, 'query': doi_name })

    else:
        return render(request, 'home/doi.html')
#Search for DOI ends!


#Search for DOI ends!


#searchByAuthor START HERE
def searchByAuthor(request):
    if 'author_name' in request.GET and request.GET['author_name']:
        page = request.GET.get('page', 1)

      

        author_name = request.GET['author_name']

        obj = Cross.objects.all()
        main_author = []
        try:
            for i in obj:
                for j in i.author:
                    auth_obj = {
                    'author_name':'',
                    'doi': '',
                    'title': '',
                    'publisher': '',
                    'issn': [],
                    'funder': [],
                    'reference': ''
                    }
                    try:
                        # print(str(j['given']+' ' +j['family']))
                        new_name = str(j['given']+' ' +j['family'])
                        finding_name = new_name.find(author_name)
                        if author_name in new_name:
                            auth_obj['author_name'] = new_name
                            auth_obj['doi'] = i.doi
                            auth_obj['title'] = i.title
                            auth_obj['publisher'] = i.publisher
                            auth_obj['issn'] = i.issn
                            
                            # print(new_name)
                            for au in i.funder:
                                funder_obj={
                                    'funder_name': '',
                                    'award': ''
                                }
                                try:
                                    # au['name']
                                    funder_obj['funder_name']=au['name']
                                    # print(funder_obj)
                                    funder_obj['award'] = ','.join(au['award'])
                                except(KeyError)as e:
                                    pass
                                print(funder_obj)
                                auth_obj['funder'].append(funder_obj)
                            print(i.doi[:5])
                            ref_number = Post.objects.filter(reference__icontains=i.doi[:5]).first
                            try:
                                for re in ref_number.identifier:
                                    if re is not None and 'doi:' in re:
                                        auth_obj['reference']=re
                                    else:
                                        pass
                            except(KeyError, AttributeError)as e:
                                pass

                            main_author.append(auth_obj)
                        else:
                            pass
                    except(KeyError, TypeError)as e:
                        pass
        except(KeyError) as e :
            pass                

        post = Post.objects.all()
        for cr in post:
            for z in cr.creator:
                dry_auth_obj = {
                'author_name':'',
                'doi': '',
                'title': '',
                'reference':''
                }
                try:
                    if z is not None:
                        if author_name in z:
                            dry_auth_obj['author_name'] = z
                            dry_auth_obj['title'] = cr.title
                            dry_auth_obj['reference']=cr.reference
                            print(cr.reference)

                            for do in cr.identifier:
                                if do is not None and 'doi:' in do:
                                    dry_auth_obj['doi'] = do
                                else:
                                    pass
                            main_author.append(dry_auth_obj)
                        else:
                            pass

                except(KeyError)as e:
                    pass



            
        paginator = Paginator(main_author, 50) # Show 25 contacts per page
        word = paginator.page(page)
        # print(word)
        return render_to_response('home/author.html',
                 {'authors': word, 'query': author_name })
    else:
        return render(request, 'home/author.html')


def searchByPublisher(request):
    ''' 
        Searh by Publication
    '''
    if 'publisher_name' in request.GET and request.GET['publisher_name']:
        page = request.GET.get('page', 1)
        # print(page)

        publisher_name = request.GET['publisher_name']

        cross = Cross.objects.filter(publisher__icontains=publisher_name)
        main_publisher = []
        for c in cross:
            pub={
                'DOI':'',
                'name': '',
                'title': '',
                'funder':[],
                'award':[],
                'author': [],
                'source': 'Crossref',
                'reference': ''

            }
            pub['DOI'] = c.doi
            pub['name'] = c.publisher
            pub['title'] = c.title
            for i in c.funder:
                pub['funder'].append(i['name'])
                new_awards = ' '.join(i['award'])
                pub['award'].append(new_awards)
            for a in c.author:
                try:
                    pub['author'].append(a['given']+' '+a['family'])
                except(KeyError)as e:
                    pass

            ref = Post.objects.filter(reference__icontains=pub['DOI']).first()
            print(ref)
            if ref is not None:
                if ref.identifier is not None:
                    for k in ref.identifier:
                        if 'doi:' in k:
                            pub['reference'] = k
                        else:
                            pub['reference']='Null'
                else:
                    pass
            else:
                pass
            main_publisher.append(pub)
            # print(main_publisher)
        


        dryad = Post.objects.filter(publisher__icontains=publisher_name)
        for d in dryad:
            dy={
                'dry_doi':'',
                'name': '',
                'title':'',
                'creator': " ",
                'source': 'Dryad',
                'reference':''          
            }
            dy['name'] = d.publisher
            # print(dy['name'])
            dy['reference'] = d.reference
            dy['title'] = d.title
            for doi in d.identifier:
                if 'doi' in doi:
                    dy['dry_doi']=doi
                    # print(dy['dry_doi'])
            if d.creator is not None:
                dy['creator']=(''.join(d.creator))
            main_publisher.append(dy)
            # print(main_publisher)
            

        paginator = Paginator(main_publisher, 10) # Show 25 contacts per page
        try:
            word = paginator.page(page)
        except PageNotAnInteger:
        # If page is not an integer, deliver first page.
            word = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            word = paginator.page(paginator.num_pages)
        # print(word)
        return render_to_response('home/publisher.html',
                 {'cross': word, 'query': publisher_name })

    else:
        return render(request, 'home/publisher.html')

#searchByPublisher ENDS HERE

#searchByFunder STARTS HERE
def searchByFunder(request):
    if 'funder_name' in request.GET and request.GET['funder_name']:
        page = request.GET.get('page', 1)

        award_name = request.GET['funder_name']
        # print(funder_name)

        funder = Cross.objects.all()
        main_funder = []
        for f in funder:
            fun={
                'name':'',
                'parent_doi': '',
                'doi': '',
                'award': '',
                'title': '',
                'refer_drayd':'',
                'source': 'Crossref',
                'author': []
            }
            for t in f.funder:
                if t['award'] is not None:
                    # print(t['award'])
                    for aw in t['award']:
                        print(aw)
                        if award_name in aw:
                            try:
                                fun['name'] = t['name']
                            except(KeyError)as e:
                                fun['name'] = 'Null'

                            try:
                                fun['doi'] = t['DOI']
                            except(KeyError)as e:
                                fun['DOI']= 'Null'
                            try:
                                fun['award'] = ' , '.join(t['award'])
                            except(KeyError)as e:
                                fun['award'] = ''

                            if f.title is not None:
                                fun['title'] = f.title
                            else:
                                fun['title'] = 'Null' 

                            fun['parent_doi'] = f.doi

                            if f.author is not None: 
                                try:
                                    for au in f.author:
                                        fun['author'].append(au['given']+ ' ' +au['family'])
                                except(KeyError, Exception)as e:
                                    pass
                            else:
                                fun['author']=[]

                            print(fun['author'])

                            try:
                                post = Post.objects.filter(reference__icontains='10.1666/08092.1').first()
                                if post.identifier is not None:
                                    for dr_id in post.identifier:
                                        if 'doi:' in dr_id:
                                            fun['refer_drayd'] = dr_id
                                            # print('In drayd reference')
                                        else:
                                            fun['refer_drayd']='Null'
                                else:
                                    fun['refer_drayd']='Null'
                            except (KeyError,AttributeError) as e:
                                continue
                            main_funder.append(fun)
                            # print(main_funder)
                        else:
                            continue
        paginator = Paginator(main_funder, 50) # Show 25 contacts per page

        try:
            word = paginator.page(page)
        except PageNotAnInteger:
            word = paginator.page(1)
        except EmptyPage:
            word = paginator.page(paginator.num_pages)

        return render_to_response('home/funder.html',
                 {'funders': word, 'query': award_name })
    else:
        return render(request, 'home/funder.html')


#searchByTitle STARTS Here

def searchByTitle(request):
    if 'title_name' in request.GET and request.GET['title_name']:
        page = request.GET.get('page', 1)

        title_name = request.GET['title_name']
        # Search in Crossref
        title = Cross.objects.filter(title__icontains=title_name)
        # print(title)
        main_title = []
        for t in title:
            tit={
                'title':'',
                'doi': '',
                'funder': [],
                'author': '',
                'publisher': '',
                'source':'Crossref',
                'reference': '',
                'refer_zenodo':''
            }

            tit['title'] = t.title

            try:
                if t.doi is not None:
                    tit['doi'] = t.doi
                    print('doi',tit['doi'])
                    #post = Post.objects.filter(reference__icontains=(tit['doi'])).first()
                    post = Post.objects.filter(reference__icontains=(tit['doi'][:5])).first()
                    if post is not None:
                        for m in post.identifier:
                            if 'doi:' in m:
                                tit['reference']=m
                            else:
                                pass
                    else:
                        pass

                    zen_records = Zen.objects.filter(doi__icontains=(tit['doi'])).first()
                    if zen_records is not None:
                        tit['refer_zenodo'] = zen_records.doi
                    else:
                        tit['refer_zenodo']=''
                else:
                    pass
            except(KeyError)as e:
                pass

            try:
                if t.funder is not None:
                    for f in t.funder:
                        fund={
                            'name': '',
                            'award': ''
                        }
                        try:
                            fund['name']= f['name']
                            fund['award'] = ', '.join(str(x) for x in f['award'])
                        except(KeyError)as e:
                            pass
                        tit['funder'].append(fund)
                else:
                    pass
            except(KeyError)as e:
                pass

            try:
                if t.author is not None:
                    joining_author=[]
                    for au in t.author:
                        item = (au['given']+' '+au['family'])
                        joining_author.append(item)
                    tit['author'] = ', '.join(str(x) for x in joining_author)
                else:
                    pass
            except(KeyError)as e:
                pass

            try:
                if t.publisher is not None:
                    tit['publisher']=t.publisher
                else:
                    pass
            except(KeyError)as e:
                pass

            

            main_title.append(tit)


        #Search in Dryad
        drydT = Post.objects.filter(title__icontains=title_name)
        for dt in drydT:
            dry_obj={
                'doi':'',
                'title': '',
                'author': [],
                'source': 'Dryad',
                'reference':'' 
            }
            dry_obj['title'] = dt.title
            dry_obj['reference'] = dt.reference
            print(dry_obj['reference'])
            if dt.identifier is not None:
                for ide in dt.identifier:
                    if 'doi:' in ide:
                        dry_obj['doi']=ide
            if dt.creator is not None:
                dry_obj['author'] = ', '.join(str(x) for x in dt.creator)
            else:
                pass
            main_title.append(dry_obj)

        #search in Zenodo
        zend = Zen.objects.filter(title__icontains=title_name)
        for z in zend:
            zen_obj={
                'doi':'',
                'title':'',
                'conceptdoi':'',
                'creator': '',
                'source': 'Zenodo',
                'related_identifiers':[],
                'links': []
            }
            zen_obj['doi'] = z.doi
            zen_obj['title'] = z.title
            zen_obj['conceptdoi'] = z.conceptdoi
            zen_obj['creator']=z.creator
            if z.related_identifiers is not None:
                for re_id in z.related_identifiers:
                    relate={
                        'identifier':'',
                        'relation': ''
                    }
                    try:
                        relate['identifier'] = re_id['identifier']
                        relate['relation'] = re_id['relation']
                        zen_obj['related_identifiers'].append(relate)
                    except(KeyError,TypeError, Exception)as e:
                        pass
            else:
                pass

            if z.links is not None:
                for li in z.links:
                    link_obj = {
                        'doi':'',
                        'conceptdoi':''
                    }
                    try:
                        # print(li['doi'])
                        link_obj['doi']=li['doi']
                        link_obj['conceptdoi'] = li['conceptdoi']

                        zen_obj['links'].append(link_obj)
                        # print(zen_obj['links'])
                    except(KeyError,TypeError, Exception)as e:
                        pass
            else:
                pass
            main_title.append(zen_obj)

        paginator = Paginator(main_title, 50) # Show 25 contacts per page
        try:
            word = paginator.page(page)
        except PageNotAnInteger:
            word = paginator.page(1)
        except EmptyPage:
            word = paginator.page(paginator.num_pages)
        return render_to_response('home/title.html',
                 {'titles': word, 'query': title_name })
    else:
        return render(request, 'home/title.html')


#############################**************PREVIOUS CODES************#####################################
# searchByTitle ENDS HERE


# def get_uri_tag(tag_data):
#     if tag_data[0]=='{':
#         uri, ignore,tag = tag_data[1:].partition('}')
#     else:
#         uri=None
#         tag = tag_data.tag
#     return uri, tag

#############################**************PREVIOUS CODES************#####################################


#searchByPublisher STARTS HERE

# def searchByPublisher(request):
#     ''' 
#         Searh by Publication
#     '''
#     if 'publisher_name' in request.GET and request.GET['publisher_name']:
#         page = request.GET.get('page', 1)
#         # print(page)

#         publisher_name = request.GET['publisher_name']

#         cross = Cross.objects.filter(publisher__icontains=publisher_name)
#         main_publisher = []
#         for c in cross:
#             pub={
#                 'DOI':'',
#                 'name': '',
#                 'title': '',
#                 'funder':[],
#                 'award':[],
#                 'author': [],
#                 'source': 'Crossref',
#                 'reference': ''

#             }
#             pub['DOI'] = c.doi
#             pub['name'] = c.publisher
#             pub['title'] = c.title
#             for i in c.funder:
#                 pub['funder'].append(i['name'])
#                 new_awards = ' '.join(i['award'])
#                 pub['award'].append(new_awards)
#             for a in c.author:
#                 try:
#                     pub['author'].append(a['given']+' '+a['family'])
#                 except(KeyError)as e:
#                     pass

#             ref = Post.objects.filter(reference__icontains=pub['DOI']).first()
#             print(ref)
#             if ref is not None:
#                 if ref.identifier is not None:
#                     for k in ref.identifier:
#                         if 'doi:' in k:
#                             pub['reference'] = k
#                         else:
#                             pub['reference']='Null'
#                 else:
#                     pass
#             else:
#                 pass
#             main_publisher.append(pub)
#             # print(main_publisher)
        


#         dryad = Post.objects.filter(publisher__icontains=publisher_name)
#         for d in dryad:
#             dy={
#                 'dry_doi':'',
#                 'name': '',
#                 'title':'',
#                 'creator': " ",
#                 'source': 'Dryad',
#                 'reference':''          
#             }
#             dy['name'] = d.publisher
#             # print(dy['name'])
#             dy['reference'] = d.reference
#             dy['title'] = d.title
#             for doi in d.identifier:
#                 if 'doi' in doi:
#                     dy['dry_doi']=doi
#                     # print(dy['dry_doi'])
#             if d.creator is not None:
#                 dy['creator']=(''.join(d.creator))
#             main_publisher.append(dy)
#             # print(main_publisher)
            

#         paginator = Paginator(main_publisher, 50) # Show 25 contacts per page
#         try:
#             word = paginator.page(page)
#         except PageNotAnInteger:
#         # If page is not an integer, deliver first page.
#             word = paginator.page(1)
#         except EmptyPage:
#             # If page is out of range (e.g. 9999), deliver last page of results.
#             word = paginator.page(paginator.num_pages)
#         # print(word)
#         return render_to_response('home/publisher.html',
#                  {'cross': word, 'query': publisher_name })

#     else:
#         return render(request, 'home/publisher.html')

# def searchByPublisher(request):
#     '''
#         Searh by Publication
#     '''
#     if 'publisher_name' in request.GET and request.GET['publisher_name']:
#         page = request.GET.get('page',1)
#         publisher_name = request.GET['publisher_name']
#         print(publisher_name)
#         cross = Cross.objects.filter(publisher__icontains=publisher_name)
#         main_publisher = []
#         for c in cross:
#             pub={
#                 'DOI':'',
#                 'name': '',
#                 'funder': [],
#                 'award':[],
#                 'author': []
#
#             }
#             pub['DOI'] = c.doi
#             pub['name'] = c.publisher
#             for i in c.funder:
#                 pub['funder'].append(i['name'])
#                 new_awards = ' '.join(i['award'])
#                 pub['award'].append(new_awards)
#             for a in c.author:
#                 try:
#                     pub['author'].append(a['given']+' '+a['family'])
#                 except(KeyError)as e:
#                     continue
#             main_publisher.append(pub)
#             print(main_publisher)
#
#         paginator = Paginator(main_publisher, 2)
#
#         try:
#             word = paginator.page(page)
#         except PageNotAnInteger:
#             word = paginator.page(1)
#         except EmptyPage:
#             word = paginator.page(paginator.num_pages)
#         return render_to_response('home/publisher.html',
#                  {'cross': word, 'query': publisher_name })
#
#     else:
#         return render(request, 'home/publisher.html')

##Search OLD PUBLISHER functionality ends!


#Search for DOI
# def searchByDOI(request):
#     '''
#         Searh by Publication
#     '''
#     if 'doi_name' in request.GET and request.GET['doi_name']:
#         page = request.GET.get('page',1)
#         doi_name = request.GET['doi_name']
#         print(doi_name)
#         cross = Cross.objects.filter(doi__icontains=doi_name)
#         main_doi = []
#         for c in cross:
#             pub={
#                 'name': '',
#                 'funder': [],
#                 'award':[],
#                 'author': [],
#                 'title': ''
#                 }


#             pub['name'] = c.publisher
#             for i in c.funder:
#                 pub['funder'].append(i['name'])
#                 new_awards = ' '.join(i['award'])
#                 pub['award'].append(new_awards)
#             for a in c.author:
#                 try:
#                     pub['author'].append(a['given']+' '+a['family'])
#                 except(KeyError)as e:
#                     continue

#                 try:
#                     if doi_name in c['title']:
#                         if c.title is not None:
#                             pub['title'] = ', '.join(c['title'])
#                             print("title is :::",title)
#                         else:
#                             continue
#                     else:
#                         continue
#                 except(KeyError)as e:
#                     continue
#                 main_doi.append(pub)
#                 print(main_doi)

#         paginator = Paginator(main_doi, 2)

#         try:
#             word = paginator.page(page)
#         except PageNotAnInteger:
#             word = paginator.page(1)
#         except EmptyPage:
#             word = paginator.page(paginator.num_pages)
#         return render_to_response('home/doi.html',
#                  {'cross': word, 'query': doi_name })

#     else:
#         return render(request, 'home/doi.html')

# ##Search for author
# def searchByAuthor(request):
#     if 'author_name' in request.GET and request.GET['author_name']:
#         page = request.GET.get('page', 1)
#
#         author_name = request.GET['author_name']
#         obj = Cross.objects.all()
#         main_author = []
#         for i in obj:
#             for j in i.author:
#                 auth_obj = {
#                 'author_name':'',
#                 'doi': '',
#                 'title': [],
#                 'publisher': '',
#                 'issn': [],
#                 'funder': []
#                 }
#                 try:
#                     # print(str(j['given']+' ' +j['family']))
#                     new_name = str(j['given']+' ' +j['family'])
#                     finding_name = new_name.find(author_name)
#                     if author_name in new_name:
#                         auth_obj['author_name'] = new_name
#                         auth_obj['doi'] = i.doi
#                         auth_obj['title'] = i.title
#                         auth_obj['publisher'] = i.publisher
#                         auth_obj['issn'] = i.issn
#
#                         # print(new_name)
#                         for au in i.funder:
#                             funder_obj={
#                                 'funder_name': '',
#                                 'award': ''
#                             }
#                             try:
#                                 # au['name']
#                                 funder_obj['funder_name']=au['name']
#                                 # print(funder_obj)
#                                 funder_obj['award'] = ','.join(au['award'])
#                             except(KeyError)as e:
#                                 continue
#                             print(funder_obj)
#                             auth_obj['funder'].append(funder_obj)
#                         main_author.append(auth_obj)
#                     else:
#                         continue
#                 except(KeyError, TypeError)as e:
#                     pass
#             break
#         paginator = Paginator(main_author, 2) # Show 25 contacts per page
#         word = paginator.page(page)
#         print(word)
#         return render_to_response('home/author.html',
#                  {'authors': word, 'query': author_name })
#     else:
#         return render(request, 'home/author.html')
#Search for author ends

# #search for old funder
# def searchByFunder(request):
#     if 'funder_name' in request.GET and request.GET['funder_name']:
#         page = request.GET.get('page', 1)
#
#         funder_name = request.GET['funder_name']
#         # print(funder_name)
#
#         funder = Cross.objects.all()
#         main_funder = []
#         for f in funder:
#             fun={
#                 'name':'',
#                 'parent_doi': '',
#                 'doi': '',
#                 'award': '',
#                 'title': ''
#             }
#             for t in f.funder:
#                 # print(t)
#                 try:
#                     if funder_name in t['name']:
#                         fun['name'] = t['name']
#                         fun['doi'] = t['DOI']
#                         fun['parent_doi'] = f.doi
#                         if t['award'] is not None:
#                             fun['award'] = ', '.join(t['award'])
#                             # print(fun['award'])
#                         else:
#                             continue
#
#                         if f.title is not None:
#                             fun['title'] = ', '.join(f['title'])
#                             # print(fun['title'])
#                         else:
#                             continue
#                     else:
#                         continue
#
#                 except(KeyError)as e:
#                     continue
#                 main_funder.append(fun)
#         paginator = Paginator(main_funder, 2) # Show 25 contacts per page
#         word = paginator.page(page)
#         print(word)
#         return render_to_response('home/funder.html',
#                  {'funders': word, 'query': funder_name })
#     else:
#         return render(request, 'home/funder.html')
#search for old funer ends!

# def send_link():
#     post = Post.objects.all()
#     # post.delete()
#     links = ['http://api.datadryad.org/oai/request?verb=ListRecords&from=1980-01-01&metadataPrefix=oai_dc&set=hdl_10255_1',
#     'http://api.datadryad.org/oai/request?verb=ListRecords&from=1980-01-01&metadataPrefix=oai_dc&set=hdl_10255_2',
#     'http://api.datadryad.org/oai/request?verb=ListRecords&from=1980-01-01&metadataPrefix=oai_dc&set=hdl_10255_3',
#     'http://api.datadryad.org/oai/request?verb=listrecords&from=2010-01-01&metadataprefix=oai_dc&set=hdl_10255_dryad.148',
#     'http://api.datadryad.org/oai/request?verb=ListRecords&from=1980-01-01&metadataPrefix=oai_dc&set=hdl_10255_dryad.7872',
#     'http://api.datadryad.org/oai/request?verb=ListRecords&from=1980-01-01&metadataPrefix=oai_dc&set=hdl_10255_dryad.7871',
#     'http://api.datadryad.org/oai/request?verb=ListRecords&from=1980-01-01&metadataPrefix=oai_dc&set=hdl_10255_dryad.2027',
#     'http://api.datadryad.org/oai/request?verb=ListRecords&from=1980-01-01&metadataPrefix=oai_dc&set=hdl_10255_dryad.2171',
#     ]
#     for link in links:
#         get_data(link)
#         # return 1
#     return 1



# def listing(request):
#     contact_list = Contacts.objects.all()
#     paginator = Paginator(contact_list, 25) # Show 25 contacts per page

#     page = request.GET.get('page')
#     try:
#         contacts = paginator.page(page)
#     except PageNotAnInteger:
#         # If page is not an integer, deliver first page.
#         contacts = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range (e.g. 9999), deliver last page of results.
#         contacts = paginator.page(paginator.num_pages)

#     return render(request, 'list.html', {'contacts': contacts})

#searchByTitle
# def searchByTitle(request):
#     if 'title_name' in request.GET and request.GET['title_name']:
#         page = request.GET.get('page', 1)

#         title_name = request.GET['title_name']
#         # Search in Crossref
#         title = Cross.objects.filter(title__icontains=title_name)
#         # print(title)
#         main_title = []
#         for t in title:
#             tit={
#                 'title':'',
#                 'doi': '',
#                 'funder': [],
#                 'author': '',
#                 'publisher': '',
#                 'source':'Crossref',
#                 'refer_doi': '',
#                 'refer_zenodo':'',
#             }

#             tit['title'] = t.title

#             try:
#                 if t.doi is not None:
#                     tit['doi'] = t.doi
#                     print(tit['doi'][:15])
#                     post = Post.objects.filter(reference__icontains=(tit['doi'])).first()
#                     if post is not None:
#                         for m in post.identifier:
#                             if 'doi:' in m:
#                                 tit['refer_doi']=m
#                             else:
#                                 pass
#                     else:
#                         pass

#                     zen_records = Zen.objects.filter(doi__icontains=(tit['doi'])).first()
#                     if zen_records is not None:
#                         tit['refer_zenodo'] = zen_records.doi
#                     else:
#                         tit['refer_zenodo']=''
#                 else:
#                     pass
#             except(KeyError)as e:
#                 pass

#             try:
#                 if t.funder is not None:
#                     for f in t.funder:
#                         fund={
#                             'name': '',
#                             'award': ''
#                         }
#                         try:
#                             fund['name']= f['name']
#                             fund['award'] = ', '.join(str(x) for x in f['award'])
#                         except(KeyError)as e:
#                             continue
#                         tit['funder'].append(fund)
#                 else:
#                     continue
#             except(KeyError)as e:
#                 continue

#             try:
#                 if t.author is not None:
#                     joining_author=[]
#                     for au in t.author:
#                         item = (au['given']+' '+au['family'])
#                         joining_author.append(item)
#                     tit['author'] = ', '.join(str(x) for x in joining_author)
#                 else:
#                     continue
#             except(KeyError)as e:
#                 continue

#             try:
#                 if t.publisher is not None:
#                     tit['publisher']=t.publisher
#                 else:
#                     continue
#             except(KeyError)as e:
#                 continue
#             main_title.append(tit)


#         #Search in Dryad
#         drydT = Post.objects.filter(title__icontains=title_name)
#         for dt in drydT:
#             dry_obj={
#                 'doi':'',
#                 'title': '',
#                 'author': [],
#                 'source': 'Dryad',
#                 'reference':''
#             }
#             dry_obj['title'] = dt.title
#             dry_obj['reference'] = dt.reference
#             if dt.identifier is not None:
#                 for ide in dt.identifier:
#                     if 'doi:' in ide:
#                         dry_obj['doi']=ide
#             if dt.creator is not None:
#                 dry_obj['author'] = ', '.join(str(x) for x in dt.creator)
#             else:
#                 continue
#             main_title.append(dry_obj)

#         #search in Zenodo
#         zend = Zen.objects.filter(title__icontains=title_name)
#         for z in zend:
#             zen_obj={
#                 'doi':'',
#                 'title':'',
#                 'conceptdoi':'',
#                 'creator': '',
#                 'source': 'Zenodo',
#                 'related_identifiers':[],
#                 'links': []
#             }
#             zen_obj['doi'] = z.doi
#             zen_obj['title'] = z.title
#             zen_obj['conceptdoi'] = z.conceptdoi
#             zen_obj['creator']=z.creator
#             if z.related_identifiers is not None:
#                 for re_id in z.related_identifiers:
#                     relate={
#                         'identifier':'',
#                         'relation': ''
#                     }
#                     try:
#                         relate['identifier'] = re_id['identifier']
#                         relate['relation'] = re_id['relation']
#                         zen_obj['related_identifiers'].append(relate)
#                     except(KeyError,TypeError, Exception)as e:
#                         continue
#             else:
#                 continue

#             if z.links is not None:
#                 for li in z.links:
#                     link_obj = {
#                         'doi':'',
#                         'conceptdoi':''
#                     }
#                     try:
#                         # print(li['doi'])
#                         link_obj['doi']=li['doi']
#                         link_obj['conceptdoi'] = li['conceptdoi']

#                         zen_obj['links'].append(link_obj)
#                         # print(zen_obj['links'])
#                     except(KeyError,TypeError, Exception)as e:
#                         continue
#             else:
#                 continue
#             main_title.append(zen_obj)

#         # print(main_title)
#         # main_title.sort(key=operator.attrgetter("doi"), reverse=False)
#         paginator = Paginator(main_title, 50) # Show 25 contacts per page
#         try:
#             word = paginator.page(page)
#         except PageNotAnInteger:
#             word = paginator.page(1)
#         except EmptyPage:
#             word = paginator.page(paginator.num_pages)
#         # print(word)
#         return render_to_response('home/title.html',
#                  {'titles': word, 'query': title_name })
#         # return render_to_response('home/title.html',
#         #          {'titles': sorted(word), 'query': title_name })
#         # sorted(results_dict.items())
#     else:
#         return render(request, 'home/title.html')
