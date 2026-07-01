## 12th June, 2026: The idea was born!

**08:32 PM:**
So, before I begin, let me say that I've always been very fond of mechanical displays... the way they work, operate, and make sounds is super cool to me. I saw "Flip Dot Display" mentioned on the hardware, I was amazed and pretty much decided that THIS right here is what im gonna build for open sauce.

I was thinking maybe I could make a gameboy type controller but render everything on the big flip disc display? we can have games like: snake, tetris, connect4 etc..

I also some some cool switches on robu (easily accessible online hardware store) few days ago so maybe i can use that for a joystick???

screenshot_flipdot_outpost_project_list

**9:58 PM:**
Okay, before i start, i decided maybe i should look for the parts i wanna use and the key part was the flip dot display itself, I looked it up, but couldn't find it anyhwere. i saw lots of videos and stuff but the purchase part was tricky.

apaprently, they were used in buses because the LEDs were not bright enough and they were pretty loud if on large scale. there was this company which sells them but ONLY if you have a valid transportation license or own multiple buses, which I clearly don't....

I looked up flipo.io (the one site mentioned in the flipdot reference image) but apparently they only have a croudfunding link and no further details

there's another site which is flipdots.com but their flip dots are kinda expensive. im not sure if the project budget allows me to get that...

> **total time spent: 3.5hrs**

---



## 13th June, 2026: I figured out I can build my own!!

**06:32 AM:**
I pretty much stayed up all night today trying to figure out my situation. I tried to find places where i can purchase, even looked up ebay but had no luck.

Big chunk of my time was spent in trying to understand how these things work, how they come together and understanding the mechanics... I saw a couple of videos where people build stuff with these flip dot displays but eventually everyhting would lead me to this one answer about where did they get it from: 1) bought from flipdots.com, or 2) found on sale on ebay.. neither of the things worked for me however I realised it's kind of not that difficult to build one on your own.. 

I tried to collect and review every single resource I could find that could be helpful to my case.. 

[https://flipdots.cargo.site](https://flipdots.cargo.site)
[https://flipdisc.io](https://flipdisc.io)
[https://github.com/chrishemmings/flipPyDot](https://github.com/chrishemmings/flipPyDot)
[https://flipdots.com/en/home/](https://flipdots.com/en/home/)
[https://github.com/CarlRaymond/AnnaxFlipdotDriver/](https://github.com/CarlRaymond/AnnaxFlipdotDriver/)
[https://hackaday.io/project/202125-fliphex-3d-printed-flip-dots/log/237704-project-log-0-preface-and-previous-experiments](https://hackaday.io/project/202125-fliphex-3d-printed-flip-dots/log/237704-project-log-0-preface-and-previous-experiments) 
[https://hackaday.io/project/189878-flip-disc-display-how-it-works-how-it-is-built](https://hackaday.io/project/189878-flip-disc-display-how-it-works-how-it-is-built)
[https://pierremuth.wordpress.com/2021/02/17/flipping-dots-fast/](https://pierremuth.wordpress.com/2021/02/17/flipping-dots-fast/)

a demonstration image which helped me understand the module better
![[rough_demo_flipdisc.png]]
by this time, i had a good understanding of what to do and realised i can actually do this. 

**08:24 AM**
I found a reference single flip disc module case online, made a 3x3 verison of it and sent it for printing... this seemed to had some issues but im fine with it.. i just wanna get my hands on something that works ASAP!!

> **total time spent: 5hrs**

---



### 14th June, 2026: first variation of the case..

**10:30 AM:**
I wasn't able to get my prints last night, but they just arrived and here's how it looks: 
![[first-3d-printed-draft.png]]
this was a simple print, but it has some flaws...

- the discs collide with each other in some scenarios
- the holes are not big enough to install a good EM base
- the friction was bad when the disc was supposed to spin
- discs would fall and slip out easily
- there was no magnet mount on the disc
- the weight distribution was imperfect

I played around with it for quite a bit.. i tried to find nails that could possibly fit in there so i could test.. there was also no place to mount the magnets and there was nothing i could have done except flip around and get an idea of how this thing works. but this has been very helpful so far

> **total time spent: 1 hr**

---



### 17th june, 2026: making MY OWN design for the module

**12:20 PM:**
I did some work on CAD, and made this one singular module for the flipdisc. this is a perfected design that im totally satisfied with... here's an attached image:
![[single_module_flipdisk.png]]
I decided to go with this cuz it has the following features:

- the electromagnet base holes are designed for M3 screws, the kind which is very available in the market + perfect for something like this
- the disc has a cutout designed for easy flipping, its enclosed on the other side to limit movement to only 180degrees at maximum
- the edges are polished where needed
- the screw hole has a base on the side where we can superglue it maybe? for better hold

Once this singular module was done, I decided to make a 3x3 version alongside this
![[3x3_module_CAD.png]]

> **total time spent: 4.5 hr**s

---



### 18th June, 2026: making an electromagnet..

**10:00 PM:**
today, I spent some of my time trying to make the electromagnet work. I've never really made an electromagnet but know how one works or atleast have some basic idea... i went shopping yesterday for some hardware components, there's a big market here in bangalore with a lot of items... I went there and got some electromagnets, some nails, a dc adapter, a dc female jack.. while i was there, i also bought some copper wire for this project
![[trying_electromagnets.png]]
I felt like i had the basic components to test how an electromagnet would work and immediately got to work.. there was something wrong and I realised very late that instead of enamelled copper wire i accidentally got bare copper wire which would make the circuit short and nothing would work except the nail getting heated..

> **total time spent: 1hr**

---



### 20th Jun, 2026: the electromagnet works, but...

i ordered the right parts for my electromagnet, the correct M3 nails, proper enameled copper wire... i was lucky enough to get the items delivered by evening same day. spent time trying to see how the electromagnet works and if it was responsive enough.. it was!!! 
i was able to get it to attract items and repel the magnets but there were still a few problems i was facing:

- the magnetic effect was not as strong at the tip of the nail, that means push force wasn't enough and the disc could potentially not flip
- I also realised that the nail is not exactly soft iron (best base material for strong magnets), it was an alloy. works for testing, but not the perfect thing..
- the biggest problem, i tried to create them as two individual magnets instead of one magnet with both the rods being opposite poles.. this would allow for a stronger magnetic force and more reliable flip disc

but i think these are the biggest blockers, everything else should work properly after this (theoretically).. 

the one problem i still face is:

- how do i find a soft iron nail core
- how do i find a bearing or something of the same material that connects them

ideally i want something U shaped, or i could connect parts to make it as such and wrap the coil around it.. the biggest issue is still where to source these parts.

image:

> **total time spent: 2 hrs**

*(hey, i fell sick for a few days & got involved in other things so couldn't get to it, i feel really bad)*

---

### 29th June, 2026: starting from where i left off..







---

### 30th June, 2026: gathering the PCB parts

**09:20 PM:**
i decided to experiment around more with the electromagnet and realised a few things are off about the kind of base i am using for the EM.. the problem is: the magnetic effect would still exist even if we cut off power supply. for a flip dot display, i would ideally want something which immediately turns off or something.. the push force needs to be strong enough... 
![[Pasted image 20260701005922.png|204]]

anyways.. majority of the mechanical things have been tested and figured out now. i will find sources for soft iron electromagnetic core but i should start building the actual PCB itself so i can get it on time...

**11:05 PM:**
I started the work on schematics just now, this is the list of components that i will have in my pcb:
(writing here too as i move on)

- [Raspberry Pi Pico 2 W](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html#pico2) (it has wireless comms, powerful enough, good for this project)
- [TB6612FNG](https://cdn.sparkfun.com/datasheets/Robotics/TB6612FNG.pdf) (dual H-bridge, allows reversing the polarity to flip electromagnet poles)
- [74HC595](https://www.ti.com/lit/ds/symlink/sn74hc595.pdf) (8-bit serial-in, parallel-out shift register IC. It acts as a digital pin expander)
- [SS34 Schottky](https://www.vishay.com/docs/88751/ss32.pdf) (reverse-polarity protection, series on +12V)
- [Recom R-78E5.0](https://recom-power.com/pdf/Innoline/R-78E-1.0.pdf) (12→5V switching reg, drop-in, 1A, no heatsink)
- [SS14 Schottky](https://www.vishay.com/docs/88746/ss12.pdf) (prevents backfeeding, makes the pcb usb safe even when power plugged in)

these things above are the key components the schematic is gonna have. i plan to have a 12V 5A dc adapter to power this thing. some other basic components that will be present in the PCB are:

- buttons (to control the flipdot display, maybe some presets, one to clear up the screen)
- a RGB led (usually stays green, goes red when the flipdots are transitioning, good feedback)
- lots of capacitors and resistors (duh)
- screw terminal (easily removable, easy to connect things)
- a fuse (i dont want to blow up the pcb if something goes wrong)

> **total time spent: 2.5hrs**

---

### July 1st, 2026: 

**11:30 AM:**
good morning, woke up pretty late, but I do somewhat have a plan to work on now. need to get started on the PCB asap. the plan is to wrap up the schematics within 2 days.. it should be done and ready. we spend another 1 day on routing and pcb work and ship it ASAP!!
