# Cicada

Synchronize your music across multiple devices in just a few clicks

## Installation

```bash
git clone https://github.com/n1teshy/cicada.git
```

## Usage

```bash
# python run.py <host> <port> <music_dir>
python run.py 0.0.0.0 8080 ./music_directory
```

### Cicada can be used in two ways

1. vanilla mode: by running the above command you make the audio files in the `music_directory` available to anyone in the same network as you on the address `<your-ip>:<server-port>/ui/`, they can play the music that is present on your device.
2. anybody in the network can create a hive(fancy name for group) and others can join the hive and let the host(hive creator) take the wheel, their controls(play/pause) will be disabled, their devices basically become wireless speakers for the host and anything the host plays will play on their devices, the playback is synced, the members of the hive can use the hive-chat feature to vote for specific songs and also, well, chat in the hive, every user also has a profile(name + bio) that they can set to their liking so other hive members know their taste in music.

### Vanilla mode

![Vanilla home page](https://raw.githubusercontent.com/n1teshy/cicada/refs/heads/main/images/vanilla_mode.png)

### Cicada mode

![Cicada mode steps](https://raw.githubusercontent.com/n1teshy/cicada/refs/heads/main/images/cicada_mode.png)
