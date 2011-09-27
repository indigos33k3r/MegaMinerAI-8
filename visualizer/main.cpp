#include <iostream>
#include "lib/gui/gui.h"
#include "lib/optionsmanager/optionsman.h"
#include "lib/timemanager/timeManager.h"
#include "lib/resourcemanager/resourceman.h"
#include "lib/resourcemanager/texture.h"
#include "lib/objectmanager/objectmanager.h"
#include "lib/renderer/renderer.h"
#include "lib/games/games.h"
#include "lib/resourcemanager/textureloader.h"
//#include "piracy/dupObj.h"

using namespace visualizer;

int main(int argc, char *argv[])
{
  ///////////////////////////////////////////////////////////////////
  // Must initialize things based on their dependency graphs
  ///////////////////////////////////////////////////////////////////

  ///////////////////////////////////////////////////////////////////
  // Options Manager Depends On Mutex
  ///////////////////////////////////////////////////////////////////
  OptionsMan->setup();

#ifdef Q_WS_MAC
	if( !OptionsMan->loadOptionFile( "../../../options.cfg" ) )
#else
	if( !OptionsMan->loadOptionFile( "./options.cfg" ) )
#endif
	{
		std::cerr << "Could Not Load options.cfg" << std::endl;
		return 1;
	}

	// initialize global options
	OptionsMan->addInt("numTurns",1);
	OptionsMan->addBool("sliderDragging", false );
	OptionsMan->addInt( "currentTurn", 0 );

  ///////////////////////////////////////////////////////////////////
  // Time Manager Depends On Options Manager
  ///////////////////////////////////////////////////////////////////

  TimeManager->setup();

  ///////////////////////////////////////////////////////////////////
  // ObjectManager depends on OptionsManager 
  ///////////////////////////////////////////////////////////////////
  ObjectManager->setup();

  ///////////////////////////////////////////////////////////////////
  // GUI Depends On This Runing, but it doens't depend on anything.
  ///////////////////////////////////////////////////////////////////
	QApplication app( argc, argv );

  ///////////////////////////////////////////////////////////////////
  // SelectionRender depends on OptionsManager 
  ///////////////////////////////////////////////////////////////////
  SelectionRender->setup();

  ///////////////////////////////////////////////////////////////////
  // Resource Manager depends on _______________________
  ///////////////////////////////////////////////////////////////////
  ResourceMan->setup();

  ///////////////////////////////////////////////////////////////////
  // Initialize Texture Loader
  ///////////////////////////////////////////////////////////////////
  TextureLoader->setup();

  ///////////////////////////////////////////////////////////////////
  // Initialize Animation Engine
  ///////////////////////////////////////////////////////////////////
  AnimationEngine->setup();

  ///////////////////////////////////////////////////////////////////
  // GUI Depends On Options Manager, Time Manager, Objectmanager,
  // SelectionRender, and QApplication running already.
  // GUI also depends on the renderer, but starts it automagically.
  ///////////////////////////////////////////////////////////////////
	GUI->setup();

  ///////////////////////////////////////////////////////////////////
  // Initalize the Games
  // This MUST be initialized last, but before loading a gamelog
  // This assigns all the pointers to the interfaces and so all
  // the the interfaces must be set up already.
  ///////////////////////////////////////////////////////////////////
  Games->setup();

	if( argc > 1 )
	{
	    GUI->loadGamelog( argv[1] );
	}

  TimeManager->timerStart();

	int retval = app.exec();

  Games->destroy();
  AnimationEngine->destroy();
  TextureLoader->destroy();
  ResourceMan->destroy();

  GUI->destroy();
	Renderer->destroy();
  ObjectManager->destroy();
  TimeManager->destroy();
	OptionsMan->destroy();

	return retval;
}

