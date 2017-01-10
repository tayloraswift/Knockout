import PackageDescription

let package = Package(name: "Swiftgron",
                targets   : [
                             Target(name: "Swiftgron", dependencies: ["Taylor", "Geometry", "SwiftCairo", "Model"]),
                             Target(name: "SwiftCairo", dependencies: ["Taylor", "Geometry"]),
                             Target(name: "Geometry", dependencies: ["Taylor"]),
                             Target(name: "Model", dependencies: ["Taylor"]),
                             Target(name: "Taylor")
                            ],
                dependencies: [.Package(url: "https://github.com/kelvin13/swiftxml.git", majorVersion: 1),
                                .Package(url: "../GLFW", majorVersion: 1),
                               .Package(url: "../SGLOpenGL", majorVersion: 1),
                               .Package(url: "../Cairo", majorVersion: 1),
                               //.Package(url: "https://github.com/SwiftGL/Image", majorVersion: 1)]
                               .Package(url: "../CJPEG", majorVersion: 1)]
                )
