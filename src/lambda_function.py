from __future__ import print_function
import base64
import json


import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import random

from pdf_parser import parser
from search import search

print('Loading function')


#TODO: Maybe add a repeat this step function

def lambda_handler(event, context):
    
    #try:
    #lambda_response = handle(event, context)
  
    spokenMsg = "<speak> Let me walk you through a safe first aid procedure. First, tell me more about the injury.</speak>"
    #spokenMsg = "<speak> " + str(event) + "</speak>"
    #return {"version": "1.0", "sessionAttributes": {}, "response": {"outputSpeech":{"type":"SSML","ssml":spokenMsg},"reprompt": {"outputSpeech": { "type": "SSML", "ssml": "<speak>Please describe the injury.</speak>" }}, "shouldEndSession":False}}
    
    return handle(event, context)

def handle(event, context):
    unsupportedPlaybackIntents = ["AMAZON.LoopOffIntent","AMAZON.LoopOnIntent","AMAZON.NextIntent","AMAZON.PreviousIntent","AMAZON.RepeatIntent","AMAZON.ShuffleOffIntent","AMAZON.ShuffleOnIntent","AMAZON.StartOverIntent"]

    

    #Example use of the pdf Parser
    #Make sure to capitalize first letter of the words + That they correspond to something in the pdf

    #steps from_pdf is a linked list - look at the structure in utilities to figure out how to parse it

    if event['request']['type']=="LaunchRequest":
      #spokenMsg = "<speak>" + str(speak) + "</speak>"
      spokenMsg = "<speak> Let me walk you through a safe first aid procedure. First, tell me what is the injury.</speak>"
      return {"version": "1.0", "sessionAttributes": {}, "response": {"outputSpeech":{"type":"SSML","ssml":spokenMsg},"reprompt": {"outputSpeech": { "type": "SSML", "ssml": "<speak>Please describe the injury.</speak>" }}, "shouldEndSession":False}}
    
 #   if "error" in event.keys():
#        return sendHelp()
        
    if event['request']['type']=="IntentRequest":
        intentName = event['request']['intent']['name']
      
        if intentName=="BurnIntent":
            speak = getInjury('Burns')
            
            print(isNewUser(event, speak))
            uploadSessionInjury(event, speak)
            spokenMsg = "<speak>" +str(speak[0])+" </speak>"
            return {"version": "1.0", "sessionAttributes": {}, "response": {"outputSpeech":{"type":"SSML","ssml":spokenMsg},"reprompt": {"outputSpeech": { "type": "SSML", "ssml": "<speak>Please describe your injury.</speak>" }}, "shouldEndSession":False}}

        elif intentName == "YesIntent":
            spokenMsg = "<speak>" + str(getConditionalNext(event))+ "</speak>"
            return {"version": "1.0", "sessionAttributes": {}, "response": {"outputSpeech":{"type":"SSML","ssml":spokenMsg},"reprompt": {"outputSpeech": { "type": "SSML", "ssml": "<speak>Please describe your injury.</speak>" }}, "shouldEndSession":False}}

        elif intentName == "NextIntent" or intentName == "NoIntent":
            spokenMsg = "<speak>" + str(getNextStep(event))+ "</speak>"
            return {"version": "1.0", "sessionAttributes": {}, "response": {"outputSpeech":{"type":"SSML","ssml":spokenMsg},"reprompt": {"outputSpeech": { "type": "SSML", "ssml": "<speak>Please describe your injury.</speak>" }}, "shouldEndSession":False}}

        elif intentName == "PreviousStepIntent":
            spokenMsg = "<speak>" + str(getPreviousStep(event))+ "</speak>"
            return {"version": "1.0", "sessionAttributes": {}, "response": {"outputSpeech":{"type":"SSML","ssml":spokenMsg},"reprompt": {"outputSpeech": { "type": "SSML", "ssml": "<speak>Please describe your injury.</speak>" }}, "shouldEndSession":False}}

        elif intentName == "StartOverIntent":
            spokenMsg = "<speak>" + str(startOver(event))+ "</speak>"
            return {"version": "1.0", "sessionAttributes": {}, "response": {"outputSpeech":{"type":"SSML","ssml":spokenMsg},"reprompt": {"outputSpeech": { "type": "SSML", "ssml": "<speak>Please describe your injury.</speak>" }}, "shouldEndSession":False}}

        elif intentName == "RepeatStepIntent":
            spokenMsg = "<speak>" + str(repeatStep(event))+ "</speak>"
            return {"version": "1.0", "sessionAttributes": {}, "response": {"outputSpeech":{"type":"SSML","ssml":spokenMsg},"reprompt": {"outputSpeech": { "type": "SSML", "ssml": "<speak>Please describe your injury.</speak>" }}, "shouldEndSession":False}}
            
        elif intentName == "DetailIntent":
            spokenMsg = "<speak>" + "Let me show you more information about the last step on your phone."
            return {"version": "1.0", "sessionAttributes": {}, "response": {"outputSpeech":{"type":"SSML","ssml":spokenMsg},"reprompt": {"outputSpeech": { "type": "SSML", "ssml": "<speak>Please describe your injury.</speak>" }}, "shouldEndSession":False}}

          
        elif intentName=="CategoryIntent":
            if event['request']['intent']['slots']['category']['value'] == 'thermal':
                spokenMsg = "<speak>" + "Can you identify if the burn is first, second, or third degree? </speak>"
            elif event['request']['intent']['slots']['category']['value'] == 'chemical':
              spokenMsg = "<speak>" + "For a chemical burn, first remove contaminated clothes. </speak>"
            elif event['request']['intent']['slots']['category']['value'] == 'electrical':
              spokenMsg = "<speak>" + "For an electrical burn, do not go near the person if they are still in contact with the power source. </speak>"
            else:
              spokenMsg = "<speak>" + " Describe the severity of your burn.</speak>"
            return {"version": "1.0", "sessionAttributes": {}, "response": {"outputSpeech":{"type":"SSML","ssml":spokenMsg},"reprompt": {"outputSpeech": { "type": "SSML", "ssml": "<speak>Please describe your injury.</speak>" }}, "shouldEndSession":False}}
        
      
        elif intentName=="GDAHelp" or intentName=="AMAZON.HelpIntent":
            return sendHelp()

        elif intentName in unsupportedPlaybackIntents:
            spokenMsg = "<speak>I can't do that with <w role=\"ivona:NN\">live</w> games.<p>I can help you with your favorite team's stats, schedule, and standings.</p> What can I help you with?</speak>"
            return {"version": "1.0", "sessionAttributes": {}, "response": {"outputSpeech":{"type":"SSML","ssml":spokenMsg}, "reprompt": {"outputSpeech": { "type": "SSML", "ssml": "<speak>You can ask me to play a live game, or you can ask about your favorite team’s stats, schedule, and more. What would you like?</speak>" }}, "shouldEndSession":False}}
    """
      elif intentName=="AMAZON.ResumeIntent":
        if isAudioPlayerPlaying(event):
          return resumePlayingGame(event)
        else:
          spokenMsg = "<speak>Sorry, no games were playing on your device. What can I help you with?</speak>"
          return {"version": "1.0", "sessionAttributes": {}, "response": {"outputSpeech":{"type":"SSML","ssml":spokenMsg}, "reprompt": {"outputSpeech": { "type": "SSML", "ssml": "<speak>You can ask me to play a live game, or you can ask about your favorite team’s stats, schedule, and more. What would you like?</speak>" }}, "shouldEndSession":False}}
        
    
      elif intentName=="AMAZON.StopIntent" or intentName=="AMAZON.PauseIntent":
        if isAudioPlayerPlaying(event):
          return {"version":"1.0", "sessionAttributes": {}, "response": { "directives" : [{ "type" : "AudioPlayer.Stop" }], "shouldEndSession":True}}
        else:
          byeByeSSML = str("<speak>Thanks.</speak>")
          return {"version":"1.0", "sessionAttributes": {}, "response":{"outputSpeech" : { "type" : "SSML", "ssml" : byeByeSSML }, "shouldEndSession":True}}
      elif intentName=="AMAZON.CancelIntent":
        byeByeSSML = str("<speak>Thanks.</speak>")
        if isAudioPlayerPlaying(event):
          return {"version":"1.0", "sessionAttributes": {}, "response":{"outputSpeech" : { "type" : "SSML", "ssml" : byeByeSSML }, "directives" : [{ "type" : "AudioPlayer.Stop" }], "shouldEndSession":True}}
        else:
          return {"version":"1.0", "sessionAttributes": {}, "response":{"outputSpeech" : { "type" : "SSML", "ssml" : byeByeSSML }, "shouldEndSession":True}}
      elif intentName == "AMAZON.Fallback" or intentName == "AMAZON.FallbackIntent":
        return sendHelp()
        
      else:
        return sendHelp()
    """


    #handle when we get a recognized intent from either our defined or the Amazon set of utterances
    #if event['request']['type']=="IntentRequest":
     #   intentName = event['request']['intent']['name']
     #   print("Intent Name: "+intentName)

 ## Example
 ##   if intentName=="":
 ##     spokenMsg = "<speak>What team's game are you interested in listening to?</speak>"
 ##     return {"version":"1.0", "sessionAttributes": {}, "response":{"outputSpeech" : { "type" : "SSML", "ssml" : spokenMsg }, "reprompt": {"outputSpeech": { "type": "SSML", "ssml": "<speak>I didn't get that. <p>What team did you want?</p></speak>" }}, "shouldEndSession":False}}
 

    
    # if we get any Amazon standard or custom GDA help utterances, we guide the user and they should respond with a repeat or (launchGame) or reprompt (teamPrompt) intent


    # handles unsupported Amazon Playback intents during playback

      
##  # handles an intentless mlb launch; intended to introduce skill and guide user
##  
##    elif event['request']['type']=="LaunchRequest":
##    welcomeSSML = "<speak>Welcome back to m.l.b. <p>You can play your favorite team’s radio broadcast, or ask me about their stats, schedule, standings, and more.</p> What can I help you with?</speak>"
##    return {"version":"1.0", "sessionAttributes": {}, "response":{"outputSpeech" : { "type" : "SSML", "ssml" : welcomeSSML }, "reprompt": {"outputSpeech": { "type": "SSML", "ssml": "<speak><p>You can ask me to play a live game, or you can ask about your favorite team’s stats, schedule, and more. What would you like?</p></speak>" }}, "shouldEndSession":False}}
##
##    # We can't respond to a SessionEndedRequest. It's just a notification.
##    elif event['request']['type']=="SessionEndedRequest":
##    return

  
def repromptUpToTwoTimes(event):
  #attempts = event.get('session', {}).get('attributes', {}).get('attempts', 0)
  attempts = event['session']['attributes']['attempts'][0]
  if attempts >= 2: return {"version": "1.0", "response": {"shouldEndSession": True}}
  else:
    prompt = "I didn't get that. <p>What team did you want?</p>"
    spokenMsg = {"type":"SSML", "ssml": "<speak>" + prompt + "</speak>"}
    return {"version": "1.0", "sessionAttributes": {"attempts": (attempts + 1)}, "response": {"outputSpeech" : spokenMsg, "shouldEndSession": False}}

def isNewUser(event, injury):
  dynamodb = boto3.resource('dynamodb')
  table = dynamodb.Table('First_Aid-Sessions')
  response = table.query(
    KeyConditionExpression=Key('User_Session').eq(str(event['session']['user']['userId']))
  )
  items = response['Items']
  
  if items:
    return False
  else:
    response = table.put_item(Item = {'User_Session':str(event['session']['user']['userId']), 'Steps':injury})
    return True

def uploadSessionInjury(event, injury):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('First_Aid-Sessions')
    response = table.update_item(Key = {'User_Session':str(event['session']['user']['userId'])},
                                 UpdateExpression="set Injury=:i, SessionId=:s, Current_Step=:c",
                                 ExpressionAttributeValues={
                                     ':i': injury,
                                     ':s': str(event['session']['sessionId']),
                                     ':c': 0
                                 },
                                 ReturnValues="UPDATED_NEW")
    print("UpdateItem succeeded:")
    #print(json.dumps(response))


def getNextStep(event): #is also conditional No (goes to default_next)
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('First_Aid-Sessions')
    try:
        response = table.get_item(
            Key={
                'User_Session': event['session']['user']['userId']})
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        item = response['Item']

        if int(item['Steps'][item['Current_Step']]['default_next']) == -1:
            return "You have reached the end of the first aid procedure. If you need, you can start over or listen to the previous step."
        else:

            response = table.update_item(Key = {'User_Session':str(event['session']['user']['userId'])},
                                         UpdateExpression="set Current_Step=:c",
                                         ExpressionAttributeValues={
                                             ':c': int(item['Steps'][item['Current_Step']]['default_next'])
                                             },
                                         ReturnValues="UPDATED_NEW")
            
            print("GetItem succeeded:")
            #print(json.dumps(item))
            
            return item['Steps'][int(item['Steps'][item['Current_Step']]['default_next'])]["Speak"]

def getConditionalNext(event):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('First_Aid-Sessions')
    try:
        response = table.get_item(
            Key={
                'User_Session': event['session']['user']['userId']})
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        item = response['Item']

        if int(item['Steps'][item['Current_Step']]['conditional_next']) == -1:
            return getNextStep(event)
        else:

            response = table.update_item(Key = {'User_Session':str(event['session']['user']['userId'])},
                                         UpdateExpression="set Current_Step=:c",
                                         ExpressionAttributeValues={
                                             ':c': int(item['Steps'][item['Current_Step']]['conditional_next'])
                                             },
                                         ReturnValues="UPDATED_NEW")
            
            print("GetItem succeeded:")
            #print(json.dumps(item))
            
            return item['Steps'][int(item['Steps'][item['Current_Step']]['conditional_next'])]["Speak"]

def getPreviousStep(event): 
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('First_Aid-Sessions')
    try:
        response = table.get_item(
            Key={
                'User_Session': event['session']['user']['userId']})
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        item = response['Item']

        if item['Current_Step'] == 0:
            return "This was the first step. If the injury is wrong, try telling me again what is your injury."
        else:

            response = table.update_item(Key = {'User_Session':str(event['session']['user']['userId'])},
                                         UpdateExpression="set Current_Step=:c",
                                         ExpressionAttributeValues={
                                             ':c': int(item['Current_Step'])-1
                                             },
                                         ReturnValues="UPDATED_NEW")
            
            print("GetItem succeeded:")
            #print(json.dumps(item))
            
            return item['Steps'][int(item['Current_Step'])-1]["Speak"]

def repeatStep(event):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('First_Aid-Sessions')
    try:
        response = table.get_item(
            Key={
                'User_Session': event['session']['user']['userId']})
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        item = response['Item']
        return item['Steps'][int(item['Current_Step'])]["Speak"]

def startOver(event):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('First_Aid-Sessions')
    try:
        response = table.get_item(
            Key={
                'User_Session': event['session']['user']['userId']})
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        item = response['Item']
        response = table.update_item(Key = {'User_Session':str(event['session']['user']['userId'])},
                                     UpdateExpression="set Current_Step=:c",
                                     ExpressionAttributeValues={
                                         ':c': 0
                                         },
                                     ReturnValues="UPDATED_NEW")
        
        return item['Steps'][0]["Speak"]
    

def getInjury(injury_text):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('First_Aid-Procedures')
    try:
        response = table.get_item(
            Key={
                "Name" : injury_text})
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        item = response['Item']
        return item['Steps']

def sendHelp():
  alexaOutputSpeech = "<speak>Please describe in a few words your injury.</speak>"
  return {"version":"1.0", "sessionAttributes": {}, "response":{"outputSpeech" : { "type" : "SSML", "ssml" : alexaOutputSpeech }, "reprompt": {"outputSpeech": { "type": "SSML", "ssml": "<speak>You can ask me to play a live game, or you can ask about your favorite team’s stats, schedule, and more. What would you like?</speak>" }}, "shouldEndSession": False}}


    
