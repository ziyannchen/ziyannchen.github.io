// get the ninja-keys element
const ninja = document.querySelector('ninja-keys');

// add the home and posts menu items
ninja.data = [{
    id: "nav-home",
    title: "Home",
    section: "Navigation",
    handler: () => {
      window.location.href = "/";
    },
  },{id: "nav-publications",
          title: "Publications",
          description: "publications by categories in reversed chronological order.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/publications/";
          },
        },{id: "news-i-started-my-intership-at-vdig-lab-peking-university",
            title: 'I started my intership at VDIG Lab, Peking University.',
            description: "",
            section: "News",},{id: "news-i-started-my-intership-at-shanghai-ai-laboratory",
            title: 'I started my intership at Shanghai AI Laboratory.',
            description: "",
            section: "News",},{id: "news-our-paper-t-sea-was-accepted-by-cvpr-2023",
            title: 'Our paper (T-SEA) was accepted by CVPR 2023.',
            description: "",
            section: "News",},{id: "news-started-a-new-journey-as-a-master-at-xpixel-group-in-the-university-of-chinese-academy-of-sciences-ucas",
            title: 'Started a new journey as a master at Xpixel group in the University...',
            description: "",
            section: "News",},{id: "news-i-started-my-internship-at-tencent-hunyuanvideo-founcation-model-team",
            title: 'I started my internship at Tencent HunyuanVideo Founcation Model team.',
            description: "",
            section: "News",},{id: "news-started-my-cs-phd-journey-at-ut-austin",
            title: 'Started my CS PhD journey at UT-Austin!',
            description: "",
            section: "News",},{
        id: 'social-github',
        title: 'GitHub',
        section: 'Socials',
        handler: () => {
          window.open("https://github.com/ziyannchen", "_blank");
        },
      },{
        id: 'social-scholar',
        title: 'Google Scholar',
        section: 'Socials',
        handler: () => {
          window.open("https://scholar.google.com/citations?user=zjrMFIIAAAAJ", "_blank");
        },
      },{
        id: 'social-email',
        title: 'email',
        section: 'Socials',
        handler: () => {
          window.open("mailto:%63%68%65%6E%7A%69%79%61%6E@%75%74%65%78%61%73.%65%64%75", "_blank");
        },
      },{
      id: 'light-theme',
      title: 'Change theme to light',
      description: 'Change the theme of the site to Light',
      section: 'Theme',
      handler: () => {
        setThemeSetting("light");
      },
    },
    {
      id: 'dark-theme',
      title: 'Change theme to dark',
      description: 'Change the theme of the site to Dark',
      section: 'Theme',
      handler: () => {
        setThemeSetting("dark");
      },
    },
    {
      id: 'system-theme',
      title: 'Use system default theme',
      description: 'Change the theme of the site to System Default',
      section: 'Theme',
      handler: () => {
        setThemeSetting("system");
      },
    },];
