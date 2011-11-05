INCLUDEPATH += ./interfaces/ \
    ./lib \
    ./common
DEPENDPATH += ./common \
    ./lib/resourcemanager/
PPATHS += ./lib/gameobject/ \
    ./lib/manager/ \
    ./lib/optionsmanager/ \
    ./lib/renderer/ \
    ./lib/resourcemanager/ \
    ./lib/timemanager/ \
    ./lib/gameobject/ \
    ./lib/gui/ \
    ./common/
SOURCES += main.cpp \
    ./lib/gameobject/*.cpp \
    ./lib/optionsmanager/*.cpp \
    ./lib/gui/*.cpp \
    ./lib/games/*.cpp \
    ./lib/timemanager/*.cpp \
    ./lib/*.cpp \
    ./lib/resourcemanager/*.cpp \
    ./lib/objectmanager/*.cpp \
    ./lib/selectionrender/*.cpp \
    ./lib/decompress/*.c \
    ./lib/renderer/*.cpp \
    ./common/*.cpp \
    ./lib/animationengine/*.cpp
MOC = moc
HEADERS += ./lib/manager/*.h \
    ./lib/timemanager/*.h \
    ./lib/gameobject/*.h \
    ./lib/optionsmanager/*.h \
    ./lib/renderer/*.h* \
    ./lib/gui/*.h \
    ./lib/objectmanager/*.h \
    ./lib/goc_controlbar.h \
    ./lib/*.h \
    ./lib/selectionrender/*.h \
    ./lib/resourcemanager/*.h \
    ./lib/animationengine/*.h \
    ./lib/decompress/*.h \
    ./common/*.h \
    ./interfaces/*.h
win32: {
#QMAKE_CFLAGS_DEBUG += -pg
#QMAKE_CXXFLAGS_DEBUG += -pg
#QMAKE_LFLAGS_DEBUG += -pg 
} else {
QMAKE_CFLAGS_DEBUG += -rdynamic
QMAKE_CXXFLAGS_DEBUG += -rdynamic
QMAKE_LFLAGS_DEBUG += -rdynamic 
}

CONFIG += release 
macx:CONFIG -= app_bundle
QT += opengl
SUBDIRS += botnet piracy lightRevelation
OTHER_FILES += 
debug:DEFINES += __DEBUG__
