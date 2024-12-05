from naoqi import ALProxy
print("Hello world")
tts = ALProxy("ALTextToSpeech", "10.42.0.134", 9559)
tts.say("Hello, world!")