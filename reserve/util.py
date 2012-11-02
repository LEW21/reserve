__version__ = "0.4"
__all__ = ["lazy"]

class lazy:
	__slots__ = ["load"]

	def __init__(self, load):
		self.load = load
		try:
			self.__doc__ = load.__doc__
		except:
			pass

	def __get__(self, obj, type=None):
		if obj is None:
			return self
		value = self.load(obj)
		setattr(obj, self.load.__name__, value)
		return value
