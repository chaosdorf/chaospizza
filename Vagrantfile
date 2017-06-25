# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.box_url = "https://atlas.hashicorp.com/ubuntu/boxes/trusty64"
  config.vm.host_name = "postgresql"
  config.vm.network "forwarded_port", guest: 5432, host: 5432
  config.vm.provision :shell, :path => "bootstrap.sh"
end
