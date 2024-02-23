from scripts.utils import load_images

DEFAULT_ALPHABETS = load_images('text/alpha',background='transparent')


class alphabets: 
    def __init__(self,text):
        self.text= text
        self.display_text = self.transform()


    def transform(self):
        text = []
        for char in self.text:
            text.append(DEFAULT_ALPHABETS[ord(char)-97])
        return text 

         

    def render(self,surf,x,y):
        count = 0
        for char in self.display_text:
            surf.blit(char,(x+count*4,y))
            count +=1