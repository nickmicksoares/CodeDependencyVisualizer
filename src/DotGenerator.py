import hashlib
import logging
#import pdb


class UmlClass:
    def __init__(self):
        self.fqn = None
        self.parents = []
        self.privateFields = []
        self.privateMethods = []
        self.publicFields = []
        self.publicMethods = []
        self.protectedFields = []
        self.protectedMethods = []

    def addParentByFQN(self, fullyQualifiedClassName):
        self.parents.append(fullyQualifiedClassName)

    def getId(self):
        return "id" + str(hashlib.md5(self.fqn).hexdigest())


class DotGenerator:
    _showPrivMembers = False
    _showProtMembers = False
    _showPubMembers = False
    _drawAssociations = False
    _drawInheritances = False

    def __init__(self):
        self.classes = {}

    def addClass(self, aClass):
        self.classes[aClass.fqn] = aClass

    def _genFields(self, accessPrefix, fields):
        ret = "".join([(accessPrefix + fieldName + ": " + fieldType + "\l") for fieldName, fieldType in fields])
        return ret

    def _genMethods(self, accessPrefix, methods):
        return "".join([(accessPrefix + methodName + methodArgs + " : " + returnType + "\l") for (returnType, methodName, methodArgs) in methods])

    def _genClass(self, aClass, withPublicMembers=False, withProtectedMembers=False, withPrivateMembers=False):
        c = (aClass.getId()+" [ \n" +
             "   label = \"{" + aClass.fqn)

        if withPublicMembers:
            pubFields = self._genFields('+ ', aClass.publicFields)
            pubMethods = self._genMethods('+ ', aClass.publicMethods)

            if len(pubFields) != 0 or len(pubMethods) != 0:
                c += "|" + pubFields + pubMethods

        if withProtectedMembers:
            protFields = self._genFields('# ', aClass.protectedFields)
            protMethods = self._genMethods('# ', aClass.protectedMethods)

            if len(protFields) != 0 or len(protMethods) != 0:
                c += "|" + protFields + protMethods

        if withPrivateMembers:
            privateFields = self._genFields('- ', aClass.privateFields)
            privateMethods = self._genMethods('- ', aClass.privateMethods)

            if len(privateFields) != 0 or len(privateMethods) != 0:
                c += "|" + privateFields + privateMethods

        c += "}\"  ]\n"
        c = c.replace('<', '\\<')
        c = c.replace('>', '\\>')
        return c

    def _genAssociations(self, aClass):
        edges = set()
        for fieldName, fieldType in aClass.privateFields:
            if fieldType in self.classes:
                c = self.classes[fieldType]
                edges.add(aClass.getId() + "->" + c.getId())
        for fieldName, fieldType in aClass.publicFields:
            if fieldType in self.classes:
                c = self.classes[fieldType]
                edges.add(aClass.getId() + "->" + c.getId())
        edgesJoined = "\n".join(edges)
        return edgesJoined+"\n" if edgesJoined != "" else ""

    def _genInheritances(self, aClass):
        edges = ""
        for parent in aClass.parents:
            if parent in self.classes:
                c = self.classes[parent]
                edges += (aClass.getId() + "->" + c.getId() + "\n")
        return edges

    def setDrawInheritances(self, enable):
        self._drawInheritances = enable

    def setDrawAssociations(self, enable):
        self._drawAssociations = enable

    def setShowPrivMethods(self, enable):
        self._showPrivMembers = enable

    def setShowProtMethods(self, enable):
        self._showProtMembers = enable

    def setShowPubMethods(self, enable):
        self._showPubMembers = enable

    # Find classes without relation
    def _find_garbage(self, associations, inheritances):
        to_be_eliminate = []
        for class_to_probe in self.classes.itervalues():
            classId = class_to_probe.getId()
            is_in_association = any(classId in s for s in associations)
            is_in_inheritance = any(classId in s for s in inheritances)
            if not (is_in_association or is_in_inheritance):
                to_be_eliminate.append(class_to_probe.getId())
        return to_be_eliminate

    def _eliminate_garbage(self, aClasses, garbage):
        for element in garbage:
            for index, value in aClasses.iteritems():
                if value.getId() == element:
                    aClasses.pop(index)
                    break
        return aClasses

    def _filter_garbage(self, content, associations, inheritances):
        # Find garbage
        classes_to_eliminate = self._find_garbage(associations, inheritances)

        # Eliminate garbage
        content = self._eliminate_garbage(content, classes_to_eliminate)

        return content

    def generate(self):

        # associations
        associations = ""
        if self._drawAssociations:
            for key, aClass in self.classes.iteritems():
                associations += self._genAssociations(aClass)

        # inheritances
        inheritances = ""
        if self._drawInheritances:
            for key, aClass in self.classes.iteritems():
                inheritances += self._genInheritances(aClass)

        # Clean classes that has no relations
        self.classes = self._filter_garbage(self.classes, associations.split('\n'), inheritances.split('\n'))

        dotContent = ("digraph dependencies {\n" +
                      "  fontname = \"Bitstream Vera Sans\"\n" +
                      "  fontsize = 8" +
                      "  node [" +
                      "    fontname = \"Bitstream Vera Sans\"\n" +
                      "    fontsize = 8\n" +
                      "    shape = \"record\"\n" +
                      "  ]\n" +
                      "  edge [\n" +
                      "    fontname = \"Bitstream Vera Sans\"\n" +
                      "    fontsize = 8\n" +
                      "  ]\n"
                      )

        for key, value in self.classes.iteritems():
            dotContent += self._genClass(value, self._showPubMembers, self._showProtMembers, self._showPrivMembers)

        if self._drawAssociations:
            if associations != "":
                dotContent += ("\nedge [arrowhead = open]\n")
                dotContent += associations


        if self._drawInheritances:
            if inheritances != "":
                dotContent += ("\nedge [arrowhead = empty]\n")
                dotContent += inheritances

        dotContent += "}\n"

        return dotContent
