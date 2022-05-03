# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/focal64"

  config.vm.define "master" do |master|
    master.vm.network "private_network", ip: "192.168.8.5"
    master.vm.hostname="master"
    master.vm.provider "virtualbox" do |v|
      v.memory = 4096
    end
  end

  config.vm.define "worker1" do |worker1|
    worker1.vm.network "private_network", ip: "192.168.8.6"
    worker1.vm.hostname="worker1"
  end

  config.vm.define "worker2" do |worker2|
    worker2.vm.network "private_network", ip: "192.168.8.7"
    worker2.vm.hostname="worker2"
  end

end
