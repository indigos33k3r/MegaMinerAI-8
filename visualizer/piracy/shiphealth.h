#ifndef SHIPHEALTH_H
#define SHIPHEALTH_H
#include "../lib/gocfamily_health.h"

class ShipHealth : public GOCFamily_Health
{
	public:
		ShipHealth(GameObject*parent, const int & currentHealth, const int & maxHealth):GOCFamily_Health(parent,currentHealth,maxHealth){}
		~ShipHealth(){}
		const GOC_IDType componentID() const {return GOC_IDType("PirateHealth");}
	private:
};
#endif													 // SHIPHEALTH_H
