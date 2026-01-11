import distro
import platform

print(distro.id())
print(distro.name())
print(distro.version())
print(distro.like())
print(distro.linux_distribution())

print(platform.system())
print(platform.release())
