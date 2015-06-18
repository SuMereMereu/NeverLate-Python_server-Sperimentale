'''
Created on 18/giu/2015

@author: nicola
'''

'''def calendar ci va il render per i professori'''
'''facciamo la struttura dati col flag uploaded? sì'''
'''bisogna che in All_Prof la chiave sia il nome usato nell'API non l'username'''
'''faccio vocabolario associazioni username nome ufficiale '''
'''nella sessione cosa mi porto, il nome ufficiale o lo username (opto per al seconda)'''
'''setting def bug temp'''

@app.route('/calendar_step1', methods=['POST', 'GET'])        #NEW SUBJECT SEARCH
def Prof_cal_step1():
    global urlAPIpolito
    global All_user
    
    if not 'prof' in session:
        return redirect(url_for('login')+"?valid=Exprd")
    
    search=""
    
    session['search_res']=[]
    search=request.form.get('search')
    
    if search == "":
        del session['search_res']
        return redirect(url_for('calendar'))
    
    APIrequest = requests.post(urlAPIpolito, json= { 'txt': search })        #COMUNICATION WITH POLITO API
    
    received=APIrequest.json()
    
    APIrequest.close()
    
    temp=[]                        
    
    if received['d']:                        #CONDITION CHECKING ELEMENTS ON RESPONSE LIST                                                            
        for element in received['d']:
            temp_obj=PolitoRequest(element['materia'], element['alfabetica'], element['docente'], element['chiave'])    #IMPORTING RESPONSE ELEMENTS
            temp.append(temp_obj)                   #LOCAL STORAGE OF RESPONSE ELEMENTS        
    
    if temp:                        #CHECK OF LOCAL DATA (IF PRESENT OR NOT)
        for subject in temp:
            flag=True
            ''' qua midava errore quando provavo a inserire una seconda materia ho fatto il ciclo col break'''
            for personal_subj in All_prof[session['prof']].subjects:            #ONLY THE SUBJECTS NOT IN THE USER'S PERSONAL DATA ARE STORED TEMPORARLY 
                if subject.code == personal_subj.code:                                    #IN THE DATABASE
                    flag = False
                    break
            if flag:
                session['search_res'].append(subject.dict_for_session())
            
        if not session['search_res']:
            return redirect(url_for('calendar')+"?select=empty")
        
        else:
            return redirect(url_for('calendar')+"?search="+search)
            
    else:
        return redirect(url_for('calendar')+"?select=empty")
    
    
    @app.route('/calendar_step2', methods=['POST', 'GET'])        #NEW SUBJECT ADDITION
def cal_step2():
    global All_user
    temp=request.form.get('subjects')
                                                                                            #TO GOOGLE PAGE ASKING FOR PERMISSION    
    if 'credentials' not in session:
        session['oauthcaller']='cal_step2'                                                                                #CHECK FOR THE USER AUTHORIZATION
        return redirect(url_for('oauth2callback'))                                #IF NOT PRESENT USER IS REDIRECTED
    
    credentials = client.OAuth2Credentials.from_json(session['credentials'])
        
    if credentials.access_token_expired:
        session['oauthcaller']='cal_step2'    
        return redirect(url_for('oauth2callback'))
            
    else:
        http_auth = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http_auth)
    
    exit = True
    
    
    for subject in session['search_res']:
        control=subject['subj']+", "+subject['alpha']+", "+subject['prof']+", quadrimestre # "+subject['code'][9]
        if control == temp and exit:                                        #IF THERE IS A MATCH BETWEEN THE SELECTED ITEM AND ANY ELEMENT IN THE TEMPORARLY SUBJECT LIST
            dict_to_obj=PolitoRequest(subject['subj'], subject['alpha'], subject['prof'], subject['code'])
            dict_to_obj.uploaded = False          
            All_user[session['prof']].subjects.append(dict_to_obj)            #TROVARE SOLUZIONE PER CARICARE OGGETTO, STORED IN DATABASE, THE SUBJECT IS ADDED IN THE USER'S OFFICIAL SUBJECT LIST
            exit = False
        
    for subject in All_prof[session['prof']].subjects:                                                        #SYNCRONIZATION WITH GOOGLE CALENDAR IS CHECKED FOR 
        if subject.uploaded == False:
            #PINGABLE SUBJECT              
            Association[subject.professor]=session['prof'] #Insert the association between prof api name and username                                                                              #EACH ELEMENT OF THE USER'S OFFICIAL SUBJECT LIST
            scheduleParameters = { 'listachiavimaterie': subject.code, 'datarif': str(date.today())}
            APIrequest = requests.post(urlScheduleTime, json=scheduleParameters)
            schedule = APIrequest.json()
            APIrequest.close()    
            if schedule['d']:
                #inviteKeyscreation
                All_prof[session['prof']].inviteKeys[subject.code]=[]
                OneWeekSpan= timedelta(7,0,0)+DateFormat(schedule['d'][0]['start'])
                for item in schedule['d']:
                    if DateFormat(item['start']) < OneWeekSpan:
                        event=PolitoCalendar()
                        event=format_schedule(item['text'])
                        event.start=item['start']
                        event.end=item['end']
                        G_cal_request= {"end":{"dateTime": event.end,"timeZone":"Europe/Rome"}, "start":{"dateTime": event.start,"timeZone":"Europe/Rome"}, "recurrence":["RRULE:FREQ=WEEKLY;UNTIL=20150631T170000Z"], "summary": event.subject+' '+event.professor, "description": event.comment, "location": event.classroom, "colorId":"3"}
                        '''modifica calendarId=All_user[session[user]].Gkey'''
                        created_event=service.events().insert(calendarId=All_prof[[session['prof']].G_key, body=G_cal_request).execute()
                        All_prof[session['prof']].inviteKeys[subject.code].append(created_event['id'])
                        subject.uploaded=True
            else:
                pass
        
            
    del session['search_res']
    return redirect(url_for('calendar'))



if __name__ == '__main__':
    