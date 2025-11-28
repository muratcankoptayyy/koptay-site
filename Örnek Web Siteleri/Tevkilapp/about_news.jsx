import React, {useEffect} from 'react';
// import { news_data } from "../../data/news_data";
import HeadLine from "../headLine";
import Image from "next/image";
import News_item from "./blog_card";
import request from '@/utils/request';

const About_news = () => {

  const [List, setList] = React.useState([]);

  const fetchData = async () => {

    const {data, success} = await request('/blog/last_posts', 'GET', null, true, false, true, 250);
    if (success) {
      let blog_datas = [];
      data.map((item) => {
        blog_datas.push({
          title: item.title,
          category: item.category.name,
          content: item.content,
          image: item.image,
          id: item.id,
          slug: item.slug,
          date: item.created_at,
        });
      });

      setList(blog_datas);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <>
      {/* <!-- Latest Posts --> */}
      <section className="relative py-24">
        <picture className="pointer-events-none absolute inset-0 -z-10 dark:hidden">
          <Image
            width={1519}
            height={773}
            priority
            src="https://cdn.tevkilapp.com/images/gradient_light.jpg"
            alt="gradient"
            className="h-full w-full object-cover"
          />
        </picture>
        <div className="container">
          {/*TODO: son haberler gelecek*/}
          <HeadLine
            text="Bizden Son Paylaşımlar"
            classes="font-display text-jacarta-700 mb-12 text-center text-3xl dark:text-white"
          />

          <News_item data={List.slice(1, 4)} />
        </div>
      </section>
      {/* <!-- end latest posts --> */}
    </>
  );
};

export default About_news;
