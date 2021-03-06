import os.path, sys, shutil, time

import tempfiles

# Permanent cache for dlmalloc and stdlibc++
class Cache:
  def __init__(self, dirname=None, debug=False):
    if dirname is None:
      dirname = os.environ.get('EM_CACHE')
    if not dirname:
      dirname = os.path.expanduser(os.path.join('~', '.emscripten_cache'))
    self.dirname = dirname
    self.debug = debug

  def ensure(self):
    shared.safe_ensure_dirs(self.dirname)

  def erase(self):
    tempfiles.try_delete(self.dirname)
    try:
      open(self.dirname + '__last_clear', 'w').write('last clear: ' + time.asctime() + '\n')
    except Exception, e:
      print >> sys.stderr, 'failed to save last clear time: ', e

  def get_path(self, shortname):
    return os.path.join(self.dirname, shortname)

  # Request a cached file. If it isn't in the cache, it will be created with
  # the given creator function
  def get(self, shortname, creator, extension='.bc'):
    if not shortname.endswith(extension): shortname += extension
    cachename = os.path.join(self.dirname, shortname)
    if os.path.exists(cachename):
      return cachename
    self.ensure()
    temp = creator()
    if temp != cachename:
      shutil.copyfile(temp, cachename)
    return cachename

# Given a set of functions of form (ident, text), and a preferred chunk size,
# generates a set of chunks for parallel processing and caching.
def chunkify(funcs, chunk_size, DEBUG=False):
  chunks = []
  # initialize reasonably, the rest of the funcs we need to split out
  curr = []
  total_size = 0
  for i in range(len(funcs)):
    func = funcs[i]
    curr_size = len(func[1])
    if total_size + curr_size < chunk_size:
      curr.append(func)
      total_size += curr_size
    else:
      chunks.append(curr)
      curr = [func]
      total_size = curr_size
  if curr:
    chunks.append(curr)
    curr = None
  return [''.join([func[1] for func in chunk]) for chunk in chunks] # remove function names

import shared
