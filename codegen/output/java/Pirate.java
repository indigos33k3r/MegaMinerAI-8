import com.sun.jna.Pointer;

///A generic pirate
class Pirate: extends Unit 
{
  Pointer ptr;
  int ID;
  int iteration;
  public Pirate(Pointer p)
  {
    ptr = p;
    ID = Client.INSTANCE.pirateGetId(ptr);
    iteration = BaseAI.iteration;
  }

  boolean validify()
  {
    if(iteration == BaseAI.iteration) return true;
    for(int i = 0; i < BaseAI.pirates.length; i++)
    {
      if(BaseAI.pirates[i].ID == ID)
      {
        ptr = BaseAI.pirates[i].ptr;
        iteration = BaseAI.iteration;
        return true;
      }
    }
    throw new ExistentialError();
  }
    
    //commands
    
  ///Move the unit to the designated X and Y coordinates
  int move(int x, int y)
  {
    validify();
    return Client.INSTANCE.pirateMove(ptr, x, y);
  }
  ///Allows a unit to display a message to the screen.
  int talk(String message)
  {
    validify();
    return Client.INSTANCE.pirateTalk(ptr, message);
  }
  ///Allows the pirate to pickup treasure on the ground.
  int pickupTreasure(int amount)
  {
    validify();
    return Client.INSTANCE.piratePickupTreasure(ptr, amount);
  }
  ///Allows the pirate to drop treasure on the groud.
  int dropTreasure(int amount)
  {
    validify();
    return Client.INSTANCE.pirateDropTreasure(ptr, amount);
  }
  ///Attempt to attack the given unit
  int attack(Unit Target)
  {
    validify();
    Target.validify();
    return Client.INSTANCE.pirateAttack(ptr, Target.ptr);
  }
    
    //getters
    
  ///Unique Identifier
  public int getId()
  {
    validify();
    return Client.INSTANCE.pirateGetId(ptr);
  }
  ///The X position of the top left corner of this object.  X is horizontal
  public int getX()
  {
    validify();
    return Client.INSTANCE.pirateGetX(ptr);
  }
  ///The Y position of the top left corner of this object.  Y is vertical
  public int getY()
  {
    validify();
    return Client.INSTANCE.pirateGetY(ptr);
  }
  ///The owner of the unit
  public int getOwner()
  {
    validify();
    return Client.INSTANCE.pirateGetOwner(ptr);
  }
  ///health of the unit
  public int getHealth()
  {
    validify();
    return Client.INSTANCE.pirateGetHealth(ptr);
  }
  ///attacking strength of the unit
  public int getStrength()
  {
    validify();
    return Client.INSTANCE.pirateGetStrength(ptr);
  }

}
