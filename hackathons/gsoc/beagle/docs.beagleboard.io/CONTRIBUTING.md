# Contributing to docs.beagleboard.io

**First off, thanks for taking the time to think about contributing!**

The following is a set of guidelines for contributing to docs.beagleboard.io, which is hosted by
the BeagleBoard.org Foundation at https://git.beagleboard.org/docs/docs.beagleboard.io. These are
mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this
document in a pull request.

## Contribution

Contributions in any form are appreciated. If you want to contribute to the docs but not sure 
where to start then you can checkout our contribution documents to help you with your first pull request.

### Code of Conduct

This project and everyone participating in it is governed by the [BeagleBoard.org Code of Conduct](https://docs.beagleboard.org/latest/intro/contribution/code-of-conduct.html). By participating, you are expected to uphold this code. Please report unacceptable behavior to [coc@bbb.io](mailto:coc@bbb.io) or contact one of the administrators on https://forum.beagleboard.org.

### Style and usage guidelines

If you are new to Sphinx, RST, or git then you can checkout out our [How can I contribute? guide](https://docs.beagleboard.org/latest/intro/contribution/how.html).

See more at https://docs.beagleboard.org/latest/intro/contribution/.

### Forking the Project

You can [fork](https://openbeagle.org/help/user/project/repository/forking_workflow.md) this project repository to create and submit changes to the documentation. BeagleBoard documentation is generated using [**Sphinx** ](https://www.sphinx-doc.org/en/master/) documentation tool. Sphinx uses the [**reStructuredText**](https://docutils.sourceforge.io/rst.html) (.rst) markup language by default. Some files are also written in [**Markdown**](https://docs.gitlab.com/ee/user/markdown.html) (.md) format. GitLab can render previews for both RST and MD files. So if you do not want to use any external tools to edit the documentation, you can do that within your browser and use the `Preview` button in GitLab to view how the changes will actually look like. 

#### Using A Browser

Using a browser is the easiest way to contribute to this project, if you are a beginner, or if your suggestions for changes are small. Though, some Git version control knowledge is preferrable. You can learn more about [Git and GitLab from here](https://openbeagle.org/help/topics/git/index.md).

You can create a fork of this repository to your GitLab account using the `Forks` button found on the main page of the project. This will create a stand-alone copy of the repository for you to work with. 

You can now edit the files without affecting the original project repository. After making the changes, you can commit (save) them and initiate a pull-request. One of the maintainers will review your changes and if accepted, will merge your changes with the original project.

#### In Local Machine

Another method is to clone the forked project into local computer and make the edits from there. If you want to take advantage of the powerful editing features of a modern IDE for writing documentation, we suggest using [**Visual Studio Code**](https://code.visualstudio.com/) for it. With an IDE, you will get syntax highlighting, linting, code completion, IntelliSense, and live preview among other things. Depending on your operating system, you need to install the following softwares or packages.

- [Visual Studio Code](https://code.visualstudio.com/)
- [Python 3](https://www.python.org/downloads/)
- [Python Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [reStructuredText Extension](https://marketplace.visualstudio.com/items?itemName=lextudio.restructuredtext)

The reStructuredText extension provides rich reStructuredText language support for VS Code. It will install everything required to work with RST files. If you are prompted for installing other recommended extensions or tools such as Python packages, just continue with their installs. The extension will also install the **Esbonio** language server for showing document previews right on the IDE.

Open the terminal of your choice and run the following command to clone the forked project to your computer. The project is saved to the location where the terminal is opened from. If you want to change the location, use `cd` command to change the directory.

```
git clone <your forked repository link>
```

Additionally, you can use the `Clone Repository` function of VS Code and paste the URL there. Wait until all of the project files are downloaded. A folder with the name `docs.beagleboard.io` will be created. You need to enter into the directory with the `cd` command. After that, you can launch VS Code from the terminal with the following command.

```
code .
```

This will open the project folder as a workspace in VS Code. If you have all the necessary tools installed, you will see an `esbonio:` status button on the status bar of VS Code. You can click it to build the Sphinx project. The build log will be printed to the `OUTPUT` window of VS Code. If you run into any issues, the output log is the place you want to look at to see what went wrong.

![Successful build of BeagleBoard docs in VS Code](/_images/BeagleBoard-Docs-on-VS-Code-Sphinx-Build-Successful.png "Successful build of BeagleBoard docs in VS Code")

VS Code is not limited to running from a folder as a workspace, or as a native application. It can run on your browser or use a remote directory as the workspace. For example, if you are on Windows 11, you can host your project on [**WSL**](https://learn.microsoft.com/en-us/windows/wsl/about) (Windows Subsystem for Linux), run an instance of VS Code in your Windows, and connect to the repository residing in the WSL. You can learn more about this from the [VS Code docs](https://code.visualstudio.com/docs/remote/wsl). This is useful if you do not want to change your main operating system to a GNU/Linux distro but still want to work with Linux-based tools.

## FAQ

* [Frequently Asked Questions category on the BeagleBoard.org Forum](https://forum.beagleboard.org/c/faq)

## Feedback

* [Site Feedback category on the BeagleBoard.org Forum](https://forum.beagleboard.org/c/site-feedback)
