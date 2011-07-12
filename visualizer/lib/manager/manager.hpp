#include "manager.h"

namespace visualizer
{

/** @brief size
 * the amount of stuff stored in the manager
 * @return The size of the manager map
 */
template < typename IdType, typename DataType >
unsigned int _Manager<IdType,DataType>::size()
{
  if (_Manager::isInit())
    m_data.size();

  return 0;
}


/** @brief clear
 * Clears all data from the manager
  @see clearPointer
  */
template < typename IdType, typename DataType >
void _Manager<IdType,DataType>::clear()
{
  if (_Manager::isInit())
    m_data.clear();
}


/** @brief exists
 * Checks to see if an item exists in the manager
 * @param id the id of the object in question
 * @return true if it exists
 */
template < typename IdType, typename DataType >
bool _Manager<IdType,DataType>::exists(const IdType & id)
{
  #if 0
  if (!_Manager::isInit())
    return false;
  #endif

  if (m_data.find(id) != m_data.end())
    return true;

  return false;
}


/** @brief del
 *	deletes an item from the manager
 * @param id the id of the object in question
 * @return true if the item in question was deleted, otherwise false
 * @see delPointers
 */
template < typename IdType, typename DataType >
bool _Manager<IdType,DataType>::del(const IdType & id)
{
  #if 0
  if (!_Manager::isInit())
    return false;
  #endif

  typename DataTable::iterator it = m_data.find(id);
  if (it == m_data.end())
    return false;

  m_data.erase(it);

  return true;
}


/** @brief reg
 * register an item into the manager
 * @param id the id the object is to have
 * @param data the value the object is to have
 * @return true if the manager is created and the object doesnt already exist
 */
template < typename IdType, typename DataType >
bool _Manager<IdType,DataType>::reg(const IdType & id, const DataType & data)
{
  typename DataTable::iterator it = m_data.find(id);
  if (it != m_data.end())
    return false;

  m_data[id] = data;
  return true;
}


/** @brief getItem
 * retrieves the object in question
 * @param id the id of the object in question
 * @return a pointer to the object or null if it doesnt exist
 */
template < typename IdType, typename DataType >
DataType * _Manager<IdType,DataType>::getItem(const IdType & id)
{

  typename DataTable::iterator it = m_data.find(id);
  if (it == m_data.end())
    return NULL;

  return &it->second;
}


/** @brief delPointer
 * deletes a pointer, only to be used if the manager is managing pointers
 * to objects and not the objects themselves
 * @param id the id of the object to delete
 * @return true if the object exists
 * @see del
 */
template < typename IdType, typename DataType >
bool _Manager<IdType,DataType>::delPointer(const IdType & id)
{
  #if 0
  if (!_Manager::isInit())
    return false;
  #endif

  typename DataTable::iterator it = m_data.find(id);
  if (it == m_data.end())
    return false;

  if (it->second != NULL)
    delete it->second;

  m_data.erase(it);

  return true;
}


/** @brief clearPointers
 * clears out the manager, only to be used if the manager
 * handles pointers and not actual objects
 * @see clear
 */
template < typename IdType, typename DataType >
void _Manager< IdType,DataType >::clearPointers()
{
  typename DataTable::iterator it = m_data.begin();
  for (;it != m_data.end(); it = m_data.begin())
  {
    if (it->second)
      delete it->second;

    m_data.erase(it);
  }

  return true;
}

} // visualizer
