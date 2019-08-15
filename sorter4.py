class Sorter:
	global reasons 
	reasons = []
	def __init__(self, dataArray):
		self.dataArray = dataArray

	def sort(self):
		reasons=[]
		if self.dataArray[0] > 20.0:
			reasons.append(" High DO Content ")
			print(" High DO Content")
		if self.dataArray[1] < -100.0 :
			reasons.append(" Negative ORP - Potential for bacteria growth ")
			print("Negative ORP - Potential for bacteria growth")
		if self.dataArray[2] < 6.5 or self.dataArray[2]>=8.5:
			reasons.append(" Abnormal pH ")
			print("Abnormal pH")
		if self.dataArray[3] > 30000.0:
			reasons.append(" Highly conductive - possible excess of salinity ")
			print("Highly conductive - possible excess of salinity")
		if self.dataArray[4] > 30.0:
			reasons.append(" Too hot - ripe for contamination ")
			print("Too hot - ripe for contamination")
		if self.dataArray[5] == 0.0:
			reasons.append(" No water flow - possible clog ")
			print("No flow of water - possible clog")
		if self.dataArray[6] > 10.0:
			reasons.append(" High nitrate content ")
			print("High nitrate content")
		if self.dataArray[7] == 3.3:
			reasons.append(" Turbid water ")
			print("Turbid water") 
		if not reasons:
			print("water safe")
		return ''.join(reasons)
