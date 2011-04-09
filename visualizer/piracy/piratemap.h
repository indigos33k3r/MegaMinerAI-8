#ifndef PIRATEMAP_H
#define PIRATEMAP_H

#include "../lib/gocfamily_render.h"
#include "../lib/parser/parser.h"
#include "../lib/resourcemanager/texture.h"
#include <string>
#include <fstream>

class PirateMap : public GOCFamily_Render
{
public:
  PirateMap();
  ~PirateMap();

  virtual const GOC_IDType componentID() const;

  void generateMap( Game& g );

  static void drawTGA( std::string filename );

  enum Orientation
  {
    horizontal,
    vertical
  };

  enum TileType
  {
    water,
    land 
  };

  int distToTile( 
      const int& x, 
      const int& y, 
      const int& mapsize,
      const TileType& type, 
      const std::map<int, Tile>& tiles
      );


  void boxBlur( 
      int **map,
      const int& width,
      const int& height,
      const int& radius );

  void blur(
      int **map,
      const int& width,
      const int& height,
      const int& radius,
      Orientation orient );

#if 0
  void findClosest( 
      int **map, 
      const int& width, 
      const int& height, 
      const int& xc, 
      const int& yc, 
      const int& rad );
#endif

  void update();
  virtual void renderAt(
      const unsigned int& turn,
      const unsigned int& frame
      );
  
private:
};

#endif
