#include "animations.h"
#include "easing_equations.h"

#include <sstream>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

namespace visualizer
{
  void StartAnim::animate( const float& t, AnimData *d )
  {
  } // StartAnim::animate()

  void DrawVirus::animate( const float& t, AnimData *d )
  {
    VirusData *vd = (VirusData*)d;
    virus &v = *m_virus;
    std:stringstream level;
    level << v.level;
    
    //Draw to check for overlapping viruses
    /*if ( v.owner == 0 )
    {
      v.renderer().setColor( Color( 1, 0.1, 0.1, .8 ) );
      v.renderer().drawQuad( vd->x+0.25, vd->y+0.25, .25, .5 );
      v.renderer().setColor( Color( 0, 0, 0 ) );
      v.renderer().drawText( vd->x+0.25, vd->y+0.25, "mainFont", level.str()  );
    }
    else
    {
      v.renderer().setColor( Color( 0.1, 0.1, 1, .8 ) );
      v.renderer().drawQuad( vd->x+0.50, vd->y+0.25, .25, .5 );
      v.renderer().setColor( Color( 0, 0, 0 ) );
      v.renderer().drawText( vd->x+0.50, vd->y+0.25, "mainFont", level.str()  );
    }*/
    
    if(v.pixels == NULL)
    {
        v.renderer().setColor( Color( 1, 1, 1 ) );
        v.renderer().drawTexturedQuad( vd->x, vd->y, 1, 1 , (v.owner ? "blue-virus" : "red-virus") );
        v.renderer().setColor( Color( 0, 1, 0 ) );
        v.renderer().drawText( vd->x+0.25, vd->y+0.25, "mainFont", level.str(), 2  );
    }
    else
    {
        v.renderer().setColor( (v.owner == 0 ? Color(1,0,0) : Color(0,0,1)) );
        
        for(int x = 0; x < 16; x++)
            for(int y = 0; y < 16; y++)
                if(v.pixels[x][y])
                {
                    //cout << "abotu to draw... ";
                    //v.renderer().drawQuad( vd->x + x/16, vd->y + y/16, 1/16, 1/16);
                    v.renderer().drawQuad( vd->x + (x * 0.0625), vd->y + (y * 0.0625), 0.0625, 0.0625);
                    //cout << "done drawing...\n";
                }
        
        v.renderer().setColor( Color(1, 1, 1) );
        v.renderer().drawText( vd->x+0.2, vd->y+0.33, "mainFont", level.str(), 2.5 );
    }
    
  } // DrawVirus::animate()

  void PushBoard::animate( const float& t, AnimData *d )
  {

    m_mb->renderer().translate( 0, m_mb->offst );


  }

  void Appear::animate( const float& t, AnimData *d )
  {
    GeneralAnim* g = (GeneralAnim*)d;

    if( t < startTime )
    {
      g->alpha = 0;
    } else
    if( t > endTime )
    {
      g->alpha = 1;
    } else
    {
      g->alpha = easeOutBounce( t-startTime, 0, 1, endTime-startTime );
    } 

    g->alpha = 1;
     

  }

  void DrawBase::animate( const float& t, AnimData *d )
  {

    GeneralAnim *g = (GeneralAnim*) d;
    base &q = *m_base;

    float intensity;
    if( t < 0.5 )
    {
      intensity = easeOutCubic( t, .8, .2, 0.5 );
    } else
    {
      intensity = easeInCubic( t-.5, 1, -.2, 0.5 );
    }

    if( q.owner == 0 )
    {
      q.renderer().setColor( Color( 0.3f*intensity, 0, 0, 1 ) ); 
    }
    else if( q.owner == 1 )
    {
      q.renderer().setColor( Color( 0, 0, 0.3f*intensity, 1 ) );
    }
    
    q.renderer().drawQuad( q.x+.1, q.y+.1, .8, .8 );
    
    q.renderer().setColor( Color( 1,1,1 ) );
    q.renderer().drawTexturedQuad( q.x, q.y, 1, 1 , (q.owner ? "blue-server" : "red-server" ) );
    
  } // DrawBase::animate()

  void DrawTile::animate( const float& t, AnimData *d )
  {

    GeneralAnim *g = (GeneralAnim*) d;
    tile &q = *m_tile;
    
    // Player 1 owned Tile
    if( q.owner == 0 )
    {
      if( q.connected() )
      {
        q.renderer().setColor( Color( 0.65, 0, 0, 0.6 ) );
        q.renderer().drawQuad( q.x, q.y, 1, 1 );
        q.renderer().setColor( Color( 0.75, 0.75, 0.75 ) );
        stringstream s;
        s << "red-nodes-" << (int)q.x%4 << "," << (int)q.y%4;
        q.renderer().drawTexturedQuad( q.x, q.y, 1, 1 , s.str() );
      }
      else
      {
        q.renderer().setColor( Color( 0.3, 0, 0, 0.5 ) );
        q.renderer().drawQuad( q.x, q.y, 1, 1 );
      }
    }// PLayer 2 owned Tile
    else if( q.owner == 1 )
    {
      if( q.connected() )
      {
        q.renderer().setColor( Color( 0, 0, 0.65, 0.6 ) );
        q.renderer().drawQuad( q.x, q.y, 1, 1 );
        q.renderer().setColor( Color( 0.75, 0.75, 0.75 ) );
        stringstream s;
        s << "blue-nodes-" << (int)q.x%4 << "," << (int)q.y%4;
        q.renderer().drawTexturedQuad( q.x, q.y, 1, 1 , s.str() );
      }
      else
      {
        q.renderer().setColor( Color( 0, 0, 0.3, 0.5 ) );
        q.renderer().drawQuad( q.x, q.y, 1, 1 );
      }
    }
    // Nobody owns this tile
    else if( q.owner == 2 )
    {
      q.renderer().setColor( Color( 0.1, 0.1, 0.1, 0.0 ) );
      q.renderer().drawQuad( q.x, q.y, 1, 1 );
    }
    // Wall Tile
    else if( q.owner == 3 )
    {
      //q.renderer().setColor( Color( 1.0, 1.0, 1.0, 0.0 ) );
      //q.renderer().drawQuad( q.x, q.y, 1, 1 );
      
      q.renderer().setColor( Color( 1.0, 1.0, 1.0 ) );
      srand(40 * q.x + q.y);
      stringstream s;
      s << "wall-" << rand()%5;
      q.renderer().drawTexturedQuad( q.x, q.y, 1, 1 , s.str() );
    }

  } // DrawTile::animate()

  void LeftAnim::animate( const float& t, AnimData *d )
  {
    VirusData *v = (VirusData*)d;
    if( t > startTime && t < endTime )
    {
      v->x = easeOutCubic( t-startTime, v->x, -1, endTime-startTime );
    } else if ( t >= endTime )
    {
      v->x--;
    }
  } // LeftAnim::animate()

  void RightAnim::animate( const float& t, AnimData *d )
  {
    VirusData *v = (VirusData*)d;
    if( t > startTime && t < endTime )
    {
      v->x = easeOutCubic( t-startTime, v->x, 1, endTime-startTime );
    } else if( t >= endTime )
    {
      v->x++;
    }
  } // RightAnim::animate() 

  void UpAnim::animate( const float& t, AnimData *d )
  {
    VirusData *v = (VirusData*)d;
    if( t > startTime && t < endTime )
    {
      v->y = easeOutCubic( t-startTime, v->y, 1, endTime-startTime );
    } else if( t >= endTime )
    {
      v->y++;
    }
  } // UpAnim::animate()

  void DownAnim::animate(const float& t, AnimData *d )
  {
    // I think this is actually up
    VirusData *v = (VirusData*)d;
    if( t > startTime && t < endTime )
    {
      v->y = easeOutCubic( t-startTime, v->y, -1, endTime-startTime );
    } else if( t >= endTime )
    {
      v->y--;
    }
  } // DownAnim::animate()


  void DrawBackground::animate( const float& t, AnimData *d )
  {
    for ( int x = 0; x < m_background->mapWidth; x += 4 )
    {
      for ( int y = 0; y < m_background->mapHeight; y+= 4 )
      {
        m_background->renderer().setColor( Color( 0.05, 0.05, 0.05 ) );
        m_background->renderer().drawQuad( x, y, 4, 4 );
        
        m_background->renderer().setColor( Color( 1.0, 1.0, 1.0 ) );
        m_background->renderer().drawTexturedQuad( x, y, 4, 4 , "nodeBackground" );
      }
    }
  } // DrawBackground::animate
  
  void DrawGrid::animate( const float& t, AnimData *d )
  {
    for(int x = 0; x < m_grid->mapWidth; x++)
    {
      m_grid->renderer().setColor( Color( 0.2, 0.2, 0.2, 0.5 ) );
      m_grid->renderer().drawLine(x, 0, x, m_grid->mapHeight, 1.0);
    }
    
    for(int y = 0; y < m_grid->mapHeight; y++)
    {
      m_grid->renderer().setColor( Color( 0.2, 0.2, 0.2, 0.5 ) );
      m_grid->renderer().drawLine(0, y, m_grid->mapWidth, y, 1.0);
    }
      
  } // DrawGrid::animate
  
  void UpCollide::animate(const float& t, AnimData *d)
  {
    VirusData *v = (VirusData*)d;
    float mid = (startTime+endTime)/2;
    
      if(t > endTime)
      {
      }
      else if (t<mid)
      {
        v->y = easeInCubic(startTime,v->y,-1,mid-startTime);
      } 
      else if (t>=mid)
      {
        v->y = easeOutCubic(mid,v->y-1,+1,endTime-mid);
      }
  } // UpCollide::animate()
  
  void DownCollide::animate(const float& t, AnimData *d)
  {
    VirusData *v = (VirusData*)d;
    float mid = (startTime+endTime)/2;
    if(t > endTime)
    {
    }
    else if(t<mid)
    {
      v->y = easeInCubic(startTime,v->y,+1,mid-startTime);
    }
    else if (t>=mid)
    {
      v->y = easeOutCubic(mid,v->y+1,-1,endTime-mid);
    }
  }

  void LeftCollide::animate(const float& t, AnimData *d)
  {
    VirusData *v = (VirusData*)d;
    float mid = (startTime+endTime)/2;
    if(t > endTime)
    {
    }
    else if(t<mid)
    {
      v->x = easeInCubic(startTime,v->x,-1,mid-startTime);
    }
    else if (t>=mid)
    {
       v->x = easeOutCubic(mid,v->x-1,+1,endTime-mid);
    }
  }
  
  void RightCollide::animate(const float& t, AnimData *d)
  {
    VirusData *v = (VirusData*)d;
    float mid = (startTime + endTime)/2;                          
    
    if(t>endTime)
    {
    }
    else if (t<mid)
    {
      v->x = easeInCubic(startTime,v->x,+1,mid-startTime);
    }
    else if (t>=mid)
    {
      v->x = easeOutCubic(mid,v->x+1,-1,endTime-mid);
    }
  }

  void DrawScore::animate( const float& t, AnimData* d )
  {
    stringstream ss;


    IRenderer::Alignment a = IRenderer::Left;
    Color team = Color( 1, 0, 0 );
    Color darkTeam = Color( 0.6, 0, 0 );
    double winningPercent = (double)m_sb->score / (double)(m_sb->score + m_sb->enemyScore);
    double startX = 0;
    double endX   = m_sb->mapWidth * winningPercent;
    double xTextOffset = 2;
    double xVirusOffset = 0.5;
    
    if( m_sb->player == 1 )
    {
      a = IRenderer::Right;
      team = Color( 0, 0, 1 );
      darkTeam = Color( 0, 0, 0.6 );
      ss << m_sb->score << " : " << m_sb->teamName;
      
      startX = m_sb->mapWidth * (1 - winningPercent);
      endX   = m_sb->mapWidth;
      xTextOffset = -2.4;
      xVirusOffset = -1.5;
    }
    else
    {
      ss << m_sb->teamName << " : " << m_sb->score;
    }

    m_sb->renderer().setColor( team ); 
    m_sb->renderer().drawText( m_sb->x + xTextOffset, m_sb->y, "mainFont", ss.str(), 3, a );
    
    for(int x = 0; x < 16; x++)
      for(int y = 0; y < 16; y++)
        if(m_sb->virusPixels[x][y])
          m_sb->renderer().drawQuad( m_sb->x + (x * 0.0625) + xVirusOffset, m_sb->y + (y * 0.0625), 0.0625, 0.0625);
    
    m_sb->renderer().drawLine(startX, m_sb->y + 1.25, endX, m_sb->y + 1.25, 16.0);
    m_sb->renderer().setColor( Color( 0.667, 0.667, 0.667) );
    m_sb->renderer().drawLine(m_sb->mapWidth/2 + 0.45, m_sb->y + 1.25, m_sb->mapWidth/2 + 0.55, m_sb->y + 1.25, 16.0);

  }

} // visualizer


