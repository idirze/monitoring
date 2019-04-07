Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-16.04"

  config.vm.network "forwarded_port", guest: 19999, host: 19999

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "tests/test.yml"
    ansible.become = true
    ansible.compatibility_mode = "2.0"
  end
end
