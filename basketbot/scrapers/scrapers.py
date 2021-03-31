import requests
from bs4 import BeautifulSoup
import bs4

class ScrapeWithClassChain:
    def __init__(self, base_id, class_chain):
        self.base_id = base_id
        self.class_chain = class_chain
        self.dom = None

    def dom_from_html(self, html):
        """
        Short Summary
        -------------
        Loads DOM from a provided string of HTML that has already been acquired.

        Extended Summary
        ----------------
        todo

        """
        self.dom = BeautifulSoup(html)
        print(self.dom.prettify())
        return self.dom

    def dom_from_url(self, url):
        """
        Short Summary
        -------------
        Loads DOM from a provided URL object.
        
        Extended Summary
        ----------------
        todo
        """
        html = requests.get(url)
        self.dom = BeautifulSoup(html)
        print(self.dom.prettify())
        return self.dom

    def scrape(self):
        """
        Short Summary
        -------------
        Scrape with loaded DOM and rules
        """
        self.__check_for_dom()
        pass

    def __check_for_dom(self):
        if self.dom is None:
            raise Exception('DOM must first be loaded using ScrapeWithClassChain.dom_from_url or ScrapeWithClassChain.dom_from_html.')

    def __elem_by_classes(self, elem, classes, dom):
        """
        Short Summary
        -------------
        Given a position in the dom and a list of classes, find all elements containing all specified classes

        Extended Summary
        ----------------
        Note that default behavior is:
        * All listed classes must be present, if only a subset are, then the DOM element is not returned.
        * A DOM element that contains these classes _and additional classes_ will be returned.
        
        Parameters
        ----------
        elem - str
            A string naming the type of element to search for (eg: "div", "a", etc...)
        classes - list(str)
            A list of class names that the desired element of type elem posseses
        dom - str
            A specification of the area of DOM to search. Must contain bs4 style attr attribute and findAll method.
        """
        if not (hasattr(dom, 'attrs') and hasattr(dom, 'findAll')):
            raise Exception('Passed DOM object must have bs4 attrs and findAll attributes')
        classes = classes if isinstance(classes, list) else [classes]
        elems = dom.findAll(elem, {"class": classes.pop()})
        
        for cls in classes:
            elems = [elem for elem in elems if cls in elem.attrs['class']]
            if len(elems)==0:
                break

        return elems


        

