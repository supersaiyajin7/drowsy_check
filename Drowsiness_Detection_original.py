from scipy.spatial import distance
from imutils import face_utils
import imutils
import dlib
import cv2
import pyttsx3
import numpy as np

detect = dlib.get_frontal_face_detector()
predict = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
engine = pyttsx3.init()

def eye_aspect_ratio(eye):
	A = distance.euclidean(eye[1], eye[5])
	B = distance.euclidean(eye[2], eye[4])
	C = distance.euclidean(eye[0], eye[3])
	ear = (A + B) / (2.0 * C)
	return ear

def get_landmarks(im):
	rects = detect(im, 1)

	if len(rects) > 1:
		return "error"
	if len(rects) == 0:
		return "error"
	return np.matrix([[p.x, p.y] for p in predict(im, rects[0]).parts()])


# def annotate_landmarks(im, landmarks):
# 	im = im.copy()
# 	for idx, point in enumerate(landmarks):
# 		pos = (point[0, 0], point[0, 1])
# 		cv2.putText(im, str(idx), pos,fontFace=cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,fontScale=0.4,color=(0, 0, 255))
# 		cv2.circle(im, pos, 3, color=(0, 255, 255))
# 	return im


def top_lip(landmarks):
    top_lip_pts = []
    for i in range(50, 53):
        top_lip_pts.append(landmarks[i])
    for i in range(61, 64):
        top_lip_pts.append(landmarks[i])
    top_lip_all_pts = np.squeeze(np.asarray(top_lip_pts))
    top_lip_mean = np.mean(top_lip_pts, axis=0)
    return int(top_lip_mean[:, 1])


def bottom_lip(landmarks):
    bottom_lip_pts = []
    for i in range(65, 68):
        bottom_lip_pts.append(landmarks[i])
    for i in range(56, 59):
        bottom_lip_pts.append(landmarks[i])
    bottom_lip_all_pts = np.squeeze(np.asarray(bottom_lip_pts))
    bottom_lip_mean = np.mean(bottom_lip_pts, axis=0)
    return int(bottom_lip_mean[:, 1])


def mouth_open(image):
    landmarks = get_landmarks(image)

    if landmarks == "error":
        return abs(0)

    #image_with_landmarks = annotate_landmarks(image, landmarks)
    top_lip_center = top_lip(landmarks)
    bottom_lip_center = bottom_lip(landmarks)
    lip_distance = abs(top_lip_center - bottom_lip_center)
    return lip_distance


def drowsy():
	thresh = 0.25
	frame_check = 5

	(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
	(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]
	cap = cv2.VideoCapture(0)
	flag = 0
	distract_count = 0
	distract_flag = 0
	while True:
		ret, frame = cap.read()
		frame = imutils.resize(frame, width=450)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		lip_distance = mouth_open(gray)
		#print("eucliean_distance:",lip_distance)
		if lip_distance < 1:
			#print("True")
			distract_count += 1
			print("distracted:", distract_count)
		if distract_count > 6:
			distract_count = 0
			distract_flag = 1

		subjects = detect(gray, 0)
		for subject in subjects:
			shape = predict(gray, subject)
			shape = face_utils.shape_to_np(shape)#converting to NumPy Array
			leftEye = shape[lStart:lEnd]
			rightEye = shape[rStart:rEnd]
			leftEAR = eye_aspect_ratio(leftEye)
			rightEAR = eye_aspect_ratio(rightEye)
			ear = (leftEAR + rightEAR) / 2.0
			#leftEyeHull = cv2.convexHull(leftEye)
			#rightEyeHull = cv2.convexHull(rightEye)
			#cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
			#cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
			if ear < thresh:
				flag += 1
				#print (flag)
				if flag >= frame_check:
					cv2.putText(frame, "****************Wake up****************", (10, 30),
						cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
					engine.say("Wake up!")
					cv2.putText(frame, "****************Please drive carefully****************", (10,325),
						cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
					engine.say("And Please drive carefully!")
					engine.runAndWait()
			else:
				flag = 0
			if lip_distance > 20:
				cv2.putText(frame,"************Stop Yawning!***********",(10,30),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
				engine.say("I think you are feeling sleepy,do you need a coffee break ?")
				engine.say("please dont yawn!")
				engine.say("please dont yawn!")
				engine.runAndWait()
				distract_count = 0

			elif lip_distance > 1:
				distract_count = 0
				#print("ld is greater than 1")

		if distract_flag == 1:
			print("Look straight please!")
			distract_flag = 0
			cv2.putText(frame, "************Look straight***********", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
						(0, 0, 255), 2)
			engine.say("Please look straight, you need to focus!")
			engine.runAndWait()

		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF
		if key == ord("q"):
			break
	cv2.destroyAllWindows()
	cap.release()



if __name__ == '__main__':
	drowsy()
