#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib2

TITLE = u'\xd61 Webradio'
PREFIX = '/music/oe1'
BASE_URL = 'http://oe1.orf.at'
ICON = 'icon-default.png'
ART = 'art-default.jpg'


def oe1feed(url):
    return json.loads(urllib2.urlopen(url).read())


def Start():
    Log('Start()')
    ObjectContainer.art = R(ART)
    DirectoryObject.thumb = R(ICON)
    ObjectContainer.title1 = TITLE
    TrackObject.thumb = R(ICON)

@handler(PREFIX, TITLE)
def Main():
    Log('Main()')
    oc = ObjectContainer()
    
    oc.add(CreateTrackObject(url='http://mp3stream3.apasf.apa.at:8000/;stream.mp3', title='Live', time=''))
    
    oc.add(
        DirectoryObject(
            key = Callback(Catchup, title=u'7 Tage'),
            title = u'7 Tage \xd61'
        )
    )
    oc.add(
        DirectoryObject(
            key = Callback(Journale, title='Journale'),
            title = 'Journale'
        )
    )

    oc.add(CreateTrackObject(url='http://mp3stream4.apasf.apa.at:8000/;stream.mp3', title='CAMPUS', time=''))
    return oc


@route(PREFIX + '/live')
def Live(title):
    Log('Live()')
    oc = ObjectContainer(title2=title)
    return oc


@route(PREFIX + '/catchup', allow_sync=True)
def Catchup(title):    
    Log('Catchup()')
    oc = ObjectContainer(title2=title)
    
    feed = oe1feed(BASE_URL + '/programm/konsole/heute')  
   
    for nav in feed['nav']:
        oc.add(
            DirectoryObject(
                key = Callback(Day, title=nav['day_label'], url=BASE_URL + nav['url']),
                title = nav['day_label']
            )
        )
    
    return oc

@route(PREFIX + '/catchup/day', allow_sync=True)
def Day(title, url):
    Log('Day(%s, %s)', title, url)
    oc = ObjectContainer(title2=title)
    
    feed = oe1feed(url)
    
    for idx, item in enumerate(feed['list'], start=1):
        oc.add(CreateTrackObject(url=item['url_stream'], title=item['title'], time=item['time']))
    
    return oc



def CreateTrackObject(url, title, time, include_container=False):
    track = TrackObject(
        key = Callback(CreateTrackObject, url=url, title=title, time=time, include_container=True),
        title = title,
        rating_key = url,
        artist=time,
        items = [
            MediaObject(
                container=Container.MP3,
                bitrate=128,
                audio_channels=2,
                audio_codec=AudioCodec.MP3,
                parts = [
                    PartObject(key=Callback(PlayAudio, url=url, ext='mp3'))
                ]
            )
        ]          
    )
    
    if include_container:
        return ObjectContainer(objects=[track])
    else:
        return track
    
    
def PlayAudio(url):
    return Redirect(url)



@route(PREFIX + '/journale', allow_sync=True)
def Journale(title):
    Log('Journale()')
    oc = ObjectContainer(title2=title)
    feed = oe1feed(BASE_URL + '/programm/konsole/journale')  
   
    for item in feed['list']:
        oc.add(CreateTrackObject(url=item['url_stream'], title=item['title'], time=item['time']))
    
    return oc



@route(PREFIX + '/campus')
def Campus(title):
    Log('Campus()')
    oc = ObjectContainer(title2=title)
    oc.add(CreateTrackObject(url='http://mp3stream4.apasf.apa.at:8000/listen.pls', title='CAMPUS', time=''))
    return oc

 
