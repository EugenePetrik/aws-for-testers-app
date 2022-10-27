from invoke import Collection
from task import deploy, destroy

namespace = Collection(deploy, destroy)