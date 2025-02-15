#ifndef APPLICATION_UTILITIES_H
#define APPLICATION_UTILITIES_H

#include "device_definition.h"
#include "protocol.h"

#define eternity ;;

#define abs(x) ((x) < 0 ? -(x) : (x))

void load_metadata(struct device_metadata_t*);

#endif
