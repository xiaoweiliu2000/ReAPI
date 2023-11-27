# ReAPI

ReAPI is a free, open knowledge base and an experimental online cloud API complementary recommendation platform for cloud API ecology. ReAPI is built to help developers easily build mashups with cloud APIs, and to help researchers explore how to build practical, user-friendly, high-performance cloud API recommendation services.

## Functionality

- Browse cloud APIs and mashups with the data recovered from ProgrammableWeb. ​An entirely new source of data is about to be added.

- Try out real-time cloud API complementary recommendations during browsing.

- Create a new mashup interactively with the experimental AI-driven tool EasyMashup, powered by cloud API complementary recommendation techniques.

- A cloud API for cloud API complementary recommendation is implemented and available for open access. The real-time load and Quality of Service (QoS) monitoring data of this cloud API is open for research.

## Component

- data_service: provide s data interface to the front end. 

- front: a web front end built with Vue 3 and Element Plus.

- rec_service: implementation of computing nodes for cloud API complementary recommendation, built with Pytorch. 

- rec_scheduler: a self-developed load balancer cosists of a cloud API to receive outside requests and send responses, the node regisration capability to manage computing nodes, and the load balancing capability to manage computing nodes. Additionally, "rec_scheduler" and "rec_service" together form the backend service for cloud API complementary recommendation.

## Deployment

All the components can be deployed with Docker. Note that before package the contents of a directory as a docker container, you may have to unzip datasets, node modules or other content, and download necessary python packages.

## Thanks

This project is developed by 528Lab, Yanshan University. 

Technical Support: Xiaowei Liu (xiaoweiliu@stumail.ysu.edu.cn), Zhen Chen (zhenchen@ysu.edu.cn)