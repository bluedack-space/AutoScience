import motion

class iOSMotionHandler():
		
	def __init__():
		pass
		
	def __del__():
		pass
	
	@staticmethod
	def getUserAcceleration():
		return motion.get_user_acceleration()
		
	@staticmethod
	def getGravity():
		return motion.get_gravity()
	
	@staticmethod
	def getAttitude():
		gravity_vectors  = motion.get_attitude()
		pitch, roll, yaw = [x for x in gravity_vectors]
		return pitch, roll, yaw
		
	@staticmethod
	def getMagneticField():
		return motion.get_magnetic_field()
