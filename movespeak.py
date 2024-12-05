from naoqi import ALProxy
motion = ALProxy("ALMotion", "169.254.178.48", 9559)
tts    = ALProxy("ALTextToSpeech", "169.254.178.48", 9559)
motion.moveInit()
motion.post.moveTo(0.2, 0, 0)
tts.say("I'm walking")