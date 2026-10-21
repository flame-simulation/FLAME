#ifndef FLAME_DATA_PATH_H
#define FLAME_DATA_PATH_H

#include <cstdlib>
#include <string>

#include <boost/filesystem.hpp>

namespace flame {

// Default lookup order for RF cavity / curve data:
//   1. DEFPATH baked in at build time (CMake -DDEF_PATH), if it exists
//   2. FLAME_DATA_DIR env var (set by `import flame` when the
//      flame-data package is installed, or exported by the user)
//   3. current directory (historical default)
// Every tier must exist to be honored, so a stale value falls
// through to the next one.
inline std::string default_eng_data_dir()
{
    namespace fs = boost::filesystem;
#ifdef DEFPATH
    if (fs::exists(DEFPATH))
        return DEFPATH;
#endif
    if (const char* env = std::getenv("FLAME_DATA_DIR")) {
        if (*env && fs::exists(env))
            return env;
    }
    return ".";
}

} // namespace flame

#endif // FLAME_DATA_PATH_H
