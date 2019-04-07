# -*- mode: ruby -*-
# # vi: set ft=ruby :

require 'fileutils'

Vagrant.require_version ">= 2.0.0"

CONFIG = File.join(File.dirname(__FILE__), "vagrant/config.rb")

COREOS_URL_TEMPLATE = "https://storage.googleapis.com/%s.release.core-os.net/amd64-usr/current/coreos_production_vagrant.json"

# Uniq disk UUID for libvirt
DISK_UUID = Time.now.utc.to_i

SUPPORTED_OS = {
  "coreos-stable" => {box: "coreos-stable",      bootstrap_os: "coreos", user: "core", box_url: COREOS_URL_TEMPLATE % ["stable"]},
  "coreos-alpha"  => {box: "coreos-alpha",       bootstrap_os: "coreos", user: "core", box_url: COREOS_URL_TEMPLATE % ["alpha"]},
  "coreos-beta"   => {box: "coreos-beta",        bootstrap_os: "coreos", user: "core", box_url: COREOS_URL_TEMPLATE % ["beta"]},
  "ubuntu-18"        => {box: "bento/ubuntu-18.04", bootstrap_os: "ubuntu", user: "vagrant"},
  "ubuntu-16"        => {box: "bento/ubuntu-16.04", bootstrap_os: "ubuntu", user: "vagrant"},
  "ubuntu-xenial64"        => {box: "ubuntu/xenial64", bootstrap_os: "ubuntu", user: "vagrant"},
  "centos"        => {box: "centos/7",           bootstrap_os: "centos", user: "vagrant"},
  "opensuse"      => {box: "opensuse/openSUSE-42.3-x86_64", bootstrap_os: "opensuse", use: "vagrant"},
  "opensuse-tumbleweed" => {box: "opensuse/openSUSE-Tumbleweed-x86_64", bootstrap_os: "opensuse", use: "vagrant"},
}

# Defaults for config options defined in CONFIG
$num_instances = 1
$instance_name_prefix = "monitoring"
$vm_gui = false
$vm_memory = 2048
$vm_cpus = 3
$shared_folders = {}
$forwarded_ports = {9090 => 9090, 3000 => 3000, 9093 => 9093, 19999 => 19999}
$subnet = "10.0.1"
$os = "centos"
$network_plugin = "flannel"
# The first three nodes are etcd servers
#etcd_instances = $num_instances
$etcd_instances = 1
# The first two nodes are kube masters
#$kube_master_instances = $num_instances == 1 ? $num_instances : ($num_instances - 1)
$kube_master_instances = 1
# All nodes are kube nodes
$kube_node_instances = $num_instances

$local_release_dir = "/vagrant/temp"

host_vars = {}

if File.exist?(CONFIG)
  require CONFIG
end

$box = SUPPORTED_OS[$os][:box]
# if $inventory is not set, try to use example
$inventory = "."

# if $inventory has a hosts file use it, otherwise copy over vars etc
# to where vagrant expects dynamic inventory to be.
if ! File.exist?(File.join(File.dirname($inventory), "hosts"))
  $vagrant_ansible = File.join(File.dirname(__FILE__), ".vagrant",
                       "provisioners", "ansible")
  FileUtils.mkdir_p($vagrant_ansible) if ! File.exist?($vagrant_ansible)
  if ! File.exist?(File.join($vagrant_ansible,"inventory"))
    FileUtils.ln_s($inventory, File.join($vagrant_ansible,"inventory"))
  end
end

if Vagrant.has_plugin?("vagrant-proxyconf")
    $no_proxy = ENV['NO_PROXY'] || ENV['no_proxy'] || "127.0.0.1,localhost"
    (1..$num_instances).each do |i|
        $no_proxy += ",#{$subnet}.#{i+10}"
    end
end

Vagrant.configure("2") do |config|
  # always use Vagrants insecure key
  config.ssh.insert_key = false
  config.vm.box = $box

  if SUPPORTED_OS[$os].has_key? :box_url
    config.vm.box_url = SUPPORTED_OS[$os][:box_url]
  end
  config.ssh.username = SUPPORTED_OS[$os][:user]
  # plugin conflict
  if Vagrant.has_plugin?("vagrant-vbguest") then
    config.vbguest.auto_update = false
  end
  (1..$num_instances).each do |i|
    config.vm.define vm_name = "%s-%02d" % [$instance_name_prefix, i] do |config|
      config.vm.hostname = vm_name
      # hostname -i returns a routable IP address
      # Vagrant uses 127.0.1.1 on Debian or Ubuntu
      #config.vm.provision :shell, inline: "sed 's/127\.0\.1\.1.*monitoring.*/#{subnet}\.0#{i} monitoring-0#{i}/' -i /etc/hosts"
      if Vagrant.has_plugin?("vagrant-proxyconf")
        config.proxy.http     = ENV['HTTP_PROXY'] || ENV['http_proxy'] || ""
        config.proxy.https    = ENV['HTTPS_PROXY'] || ENV['https_proxy'] ||  ""
        config.proxy.no_proxy = $no_proxy
      end

      $forwarded_ports.each do |guest, host|
        config.vm.network "forwarded_port", guest: guest, host: host, auto_correct: true
      end

      config.vm.synced_folder ".", "/vagrant", type: "rsync", rsync__args: ['--verbose', '--archive', '--delete', '-z']

      $shared_folders.each do |src, dst|
        config.vm.synced_folder src, dst, type: "rsync", rsync__args: ['--verbose', '--archive', '--delete', '-z']
      end

      config.vm.provider :virtualbox do |vb|
        vb.gui = $vm_gui
        if i == 1
          vb.memory = $vm_memory
          vb.cpus = 2
        else
          vb.memory = 4096
          vb.cpus = 4
        end
        vb.customize ["modifyvm", :id, "--nicpromisc3", "allow-all"]
        vb.name = vm_name
      end

     config.vm.provider :libvirt do |lv|
       lv.memory = $vm_memory
     end

      ip = "#{$subnet}.#{i+9}" # 10.0.1.10, 10.0.1.11, 10.0.1.12 ...
      host_vars[vm_name] = {
        "ip": ip,
        "bootstrap_os": SUPPORTED_OS[$os][:bootstrap_os],
        "local_release_dir" => $local_release_dir,
        "download_run_once": "False",
        "kube_network_plugin": $network_plugin
      }

      config.vm.network :private_network, ip: ip
      config.vm.network "public_network", bridge: "en0: Wi-Fi (AirPort)"

      # Disable swap for each vm
      config.vm.provision "shell", inline: "swapoff -a"
      # Add public key

      config.vm.provision "shell" do |s|
        ssh_prv_key = ""
        ssh_pub_key = ""
        if File.file?("#{Dir.home}/.ssh/id_rsa")
          ssh_pub_key = File.readlines("#{Dir.home}/.ssh/id_rsa.pub").first.strip
        else
          puts "No SSH key found. You will need to remedy this before pushing to the repository."
        end
        s.inline = <<-SHELL
          if grep -sq "#{ssh_pub_key}" /home/vagrant/.ssh/authorized_keys; then
            echo "SSH keys already provisioned."
            exit 0;
          fi
          echo "SSH key provisioning."
          mkdir -p /home/vagrant/.ssh/
          touch /home/vagrant/.ssh/authorized_keys
          echo #{ssh_pub_key} >> /home/vagrant/.ssh/authorized_keys
          chown -R vagrant:vagrant /home/vagrant
          exit 0
        SHELL
      end


      if $kube_node_instances_with_disks
        # Libvirt
        driverletters = ('a'..'z').to_a
        config.vm.provider :libvirt do |lv|
          # always make /dev/sd{a/b/c} so that CI can ensure that
          # virtualbox and libvirt will have the same devices to use for OSDs
          (1..$kube_node_instances_with_disks_number).each do |d|
            lv.storage :file, :device => "hd#{driverletters[d]}", :path => "disk-#{i}-#{d}-#{DISK_UUID}.disk", :size => $kube_node_instances_with_disks_size, :bus => "ide"
          end
        end
      end
      
      # Only execute once the Ansible provisioner,
      # when all the machines are up and ready.
      if i == $num_instances
        config.vm.provision "ansible" do |ansible|
          ansible.playbook = "cluster.yml"
          if File.exist?(File.join(File.dirname($inventory), "hosts.ini"))
            ansible.inventory_path = $inventory
          end
          ansible.inventory_path = "hosts.ini"
          ansible.become = true
          ansible.limit = "all"
          ansible.host_key_checking = false
          ansible.raw_arguments = ["--forks=#{$num_instances}", "--flush-cache"]
          #ansible.host_vars = host_vars
          #ansible.tags = ['download']
          ansible.groups = {
            "kube-master" => ["#{$instance_name_prefix}-0[1:#{$kube_master_instances}]"],
            "kube-node" => ["#{$instance_name_prefix}-0[2:#{$kube_node_instances}]"]
          }
        end
      end

    end
  end
end
