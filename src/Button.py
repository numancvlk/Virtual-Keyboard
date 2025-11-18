#LIBRARIES
import cv2

class Button:
    DEFAULT_COLOR = (150, 150, 255)  
    TEXT_COLOR = (50, 50, 50)

    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos  
        self.size = size 
        self.text = text

    def draw(self, img):
        x, y = self.pos
        w, h = self.size
        
        cv2.rectangle(img, self.pos, (x + w, y + h), self.DEFAULT_COLOR, cv2.FILLED)
        cv2.rectangle(img, self.pos, (x + w, y + h), (50, 50, 50), 3)
        
        cv2.putText(img, self.text, (x + 20, y + 65),
                    cv2.FONT_HERSHEY_PLAIN, 4, self.TEXT_COLOR, 4) 
        return img