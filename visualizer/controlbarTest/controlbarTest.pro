HEADERS += granolabar.h \
granolabutton.h
SOURCES += main.cpp \
gui.cpp \
granolabar.cpp \
granolabutton.cpp

MOC = moc
QMAKE_CFLAGS_DEBUG += -pg
QMAKE_CXXFLAGS_DEBUG += -pg
QMAKE_LFLAGS_DEBUG += -pg
CONFIG += debug
