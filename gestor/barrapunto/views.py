from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, HttpResponseNotFound
from barrapunto.models import Gestor

from xml.sax.handler import ContentHandler
from xml.sax import make_parser
import sys
import urllib.request

class myContentHandler(ContentHandler):

    def __init__ (self):
        self.inItem = False
        self.inContent = False
        self.theContent = ""
        # Al principio de todo es necesario restaurar la BBDD
        d = Gestor.objects.all()
        d.delete()

    def startElement (self, name, attrs):
        # Los datos de las páginas se encuentras tras la etiqueta 'item'.
        # Nota apararece otros 'link' y 'title' que no me interesa.
        if name == 'item':
            self.inItem = True
        elif self.inItem:
            # Esto en el contenido buscado cuando leo la etiqueta 'title' o 'link'.
            if name == 'title':
                self.inContent = True
            elif name == 'link':
                self.inContent = True
            elif name == 'description':
                self.inContent = True

    def endElement (self, name):
        # Salgo de '/item', luego ya no estoy en el contenido buscado.
        if name == 'item':
            self.inItem = False
        elif self.inItem:
            if name == 'title':
                self.line = self.theContent
                # To avoid Unicode trouble
                self.inContent = False
                self.theContent = ""
            elif name == 'link':
                self.link = "<a href='" + self.theContent + "'>" + self.line + "</a><br>"
                self.inContent = False
                self.theContent = ""
            elif name == 'description':
                self.des = self.theContent + "<br>"
                self.inContent = False
                self.theContent = ""

                # Realizo el guardado del contenido RSS en la BBDD.
                # Dicho contenido se actualizara cuando volvamos a la pagina principal.
                # Lo realicé así para mostrar al usuario un menu de los recursos = title
                new = Gestor(title = self.line, url = self.link, content = self.des)
                print(new.title)
                new.save()

    def characters (self, chars):
        # Si estoy en el contenido, añado a la varible inContent los caracteres.
        if self.inContent:
            self.theContent = self.theContent + chars




def home(request):
    theParser = make_parser()
    theHandler = myContentHandler()
    theParser.setContentHandler(theHandler)

    xmlFile = urllib.request.urlopen('http://barrapunto.com/index.rss')
    theParser.parse(xmlFile)

    titles = Gestor.objects.all()
    response = "<ul>"

    for title in titles:
            response += title.title + "<br>"
    response += "</ul>"
    return HttpResponse("<h1> Estos son los recursos que disponemos actualmente: </h1>" + response
        + "</h1><br><br><h5>Los recursos se acaban de actualizar de BarraPunto, tan sólo añade el deseado al buscador y a DISFRUTAR</h5>")


def content(request, key):
    global response

    try:
        resource = Gestor.objects.get(title=key)

        links = Gestor.objects.all()
        response = "<ul>"
        for link in links:
            response += link.url + "<br>"
        response += "</ul>"

        return HttpResponse("<h1>El contenido del recurso es: </h1><center>" + resource.content
            + "</center><h1><br>Además disponemos de otros recursos:</h1>" + response)

    except Gestor.DoesNotExist:
        return HttpResponseNotFound('<h1><center>Resource not found</center></h1>')
